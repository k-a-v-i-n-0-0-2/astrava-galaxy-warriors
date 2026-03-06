#!/usr/bin/env python3
"""
Flask Backend for ASTRAVA AI Detector — Gemini Vision Powered
"""

import os
import sys
import functools

# Force unbuffered output so all print() appears in terminal immediately
os.environ['PYTHONUNBUFFERED'] = '1'

def _log(msg: str):
    """Immediate flush logging."""
    print(msg, flush=True)

import pandas as pd
import numpy as np
import json
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from dotenv import load_dotenv
import tempfile

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.loader import InteractionDataLoader
    from src.detector import InstagramAIConfidenceLabeler
    from src.detect_service import run_detection
    print("✅ Successfully imported backend modules")
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# Disable all caching
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def get_labeler():
    gemini_key = os.getenv('GEMINI_API_KEY')
    return InstagramAIConfidenceLabeler(gemini_api_key=gemini_key)

def generate_deterministic_interactions(video_id, video_num):
    """
    Generate UNIQUE and DETERMINISTIC interactions based on video ID
    Same video ID will ALWAYS get the same pattern
    Different video IDs will get DIFFERENT patterns
    """
    
    # Use video_id to create a deterministic seed
    seed_value = int(hashlib.md5(str(video_id).encode()).hexdigest()[:8], 16)
    random_state = np.random.RandomState(seed_value)
    
    base_time = datetime.now() - timedelta(hours=2)
    interactions = []
    
    # Define DIFFERENT patterns for different video numbers
    if video_num in [1, 5, 9]:  # PATTERN A: Bot Network (High AI scores)
        print(f"   📊 Pattern A (Bot Network) for video {video_id}")
        users = [f"bot_{i:03d}" for i in range(1, 11)]
        base_minute = 0
        
        for i in range(45):  # 45 interactions
            user_idx = i % 10
            minute_offset = base_minute + (i // 3)  # Very regular timing
            
            # Create synchronized timestamps (within same second)
            second_offset = int(random_state.choice([0, 1, 2]))
            timestamp = (base_time + timedelta(minutes=minute_offset, seconds=second_offset)).strftime('%Y-%m-%d %H:%M:%S')
            
            # Action distribution skewed towards shares/reposts
            action_rand = random_state.random()
            if action_rand < 0.3:
                action = 'like'
            elif action_rand < 0.6:
                action = 'share'
            elif action_rand < 0.8:
                action = 'repost'
            else:
                action = 'comment'
            
            interactions.append({
                'user_id': users[user_idx],
                'timestamp': timestamp,
                'action_type': action
            })
    
    elif video_num in [2, 6, 10]:  # PATTERN B: Real Human (Low AI scores)
        print(f"   📊 Pattern B (Real Human) for video {video_id}")
        # 25 different real users
        minute_offsets = []
        for i in range(25):
            # Natural random distribution
            minute_offsets.append(random_state.uniform(5, 120))
        
        minute_offsets.sort()
        
        for i, minute_offset in enumerate(minute_offsets[:25]):
            user_id = f"user_{1000 + i + (video_num * 100)}"
            timestamp = (base_time + timedelta(minutes=minute_offset)).strftime('%Y-%m-%d %H:%M:%S')
            
            # Natural action distribution (mostly likes)
            action_rand = random_state.random()
            if action_rand < 0.7:
                action = 'like'
            elif action_rand < 0.85:
                action = 'comment'
            elif action_rand < 0.95:
                action = 'share'
            else:
                action = 'repost'
            
            interactions.append({
                'user_id': user_id,
                'timestamp': timestamp,
                'action_type': action
            })
    
    elif video_num in [3, 7]:  # PATTERN C: Coordinated Attack (Very High AI)
        print(f"   📊 Pattern C (Coordinated Attack) for video {video_id}")
        users = [f"attacker_{i:03d}" for i in range(1, 8)]
        
        for i in range(35):
            user_idx = i % 7
            # Extremely fast: all within 10 minutes
            minute_offset = i * 0.3  # Every 18 seconds!
            timestamp = (base_time + timedelta(minutes=minute_offset)).strftime('%Y-%m-%d %H:%M:%S')
            
            # Almost all are shares/reposts (amplification)
            action_rand = random_state.random()
            if action_rand < 0.2:
                action = 'like'
            elif action_rand < 0.6:
                action = 'share'
            elif action_rand < 0.9:
                action = 'repost'
            else:
                action = 'comment'
            
            interactions.append({
                'user_id': users[user_idx],
                'timestamp': timestamp,
                'action_type': action
            })
    
    elif video_num in [4, 8]:  # PATTERN D: Organic Spread (Low AI)
        print(f"   📊 Pattern D (Organic Spread) for video {video_id}")
        # Many unique users, spread over time
        for i in range(30):
            user_id = f"organic_{2000 + i + (video_num * 50)}"
            minute_offset = random_state.uniform(10, 180)  # Spread over 3 hours
            timestamp = (base_time + timedelta(minutes=minute_offset)).strftime('%Y-%m-%d %H:%M:%S')
            
            # Natural distribution
            action_rand = random_state.random()
            if action_rand < 0.8:
                action = 'like'
            elif action_rand < 0.9:
                action = 'comment'
            else:
                action = 'share'
            
            interactions.append({
                'user_id': user_id,
                'timestamp': timestamp,
                'action_type': action
            })
    
    else:  # Default pattern
        print(f"   📊 Default pattern for video {video_id}")
        for i in range(20):
            user_id = f"user_{3000 + i}"
            minute_offset = random_state.uniform(1, 60)
            timestamp = (base_time + timedelta(minutes=minute_offset)).strftime('%Y-%m-%d %H:%M:%S')
            
            interactions.append({
                'user_id': user_id,
                'timestamp': timestamp,
                'action_type': 'like' if random_state.random() < 0.7 else 'comment'
            })
    
    print(f"   Generated {len(interactions)} interactions for video {video_id}")
    return interactions

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

_ANALYSIS_CACHE = {}

@app.route('/api/analyze/reel', methods=['POST'])
def analyze_reel():
    """Analyze a reel with HIGH FIDELITY detection pipeline"""
    try:
        data = request.json
        reel_data = data.get('reel', {})
        frontend_interactions = data.get('interactions', [])
        
        # Get video ID
        video_id = reel_data.get('id', 'unknown')
        video_url = reel_data.get('video_url', '')
        
        # Resolve file path – check hackfusion public/ AND ASTRAVA public/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        public_dir = os.path.join(base_dir, 'public')
        # ASTRAVA public directory
        astrava_public = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ASTRAVA', 'ASTRAVA', 'public')
        
        try:
            video_num = int(video_id)
        except:
            video_num = 1
        
        print(f"\n{'='*60}")
        print(f"🔍 AUTO-ANALYZING VIDEO {video_id} at {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        # --- CACHE CHECK ---
        if video_id in _ANALYSIS_CACHE:
            print(f"   ⚡ RETURNED CACHED RESULT FOR {video_id}")
            response = jsonify(_ANALYSIS_CACHE[video_id])
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            return response

        # --- PATH RESOLUTION ---
        file_path = None
        print(f"   📥 Received video_url: '{video_url}'")
        if video_url:
            if video_url.startswith('http'):
                file_path = video_url
                print(f"   ✅ Using HTTP URL: {file_path}")
            else:
                clean_url = video_url.lstrip('./\\')
                
                if os.path.exists(video_url) and os.path.isabs(video_url):
                    file_path = video_url
                    print(f"   ✅ Found exact absolute path: {file_path}")
                else:
                    # Search order: local public → ASTRAVA public → root public → app.py dir
                    search_dirs = [
                        ('local public', public_dir),
                        ('ASTRAVA public', astrava_public),
                        ('root public', os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'public')),
                        ('app.py dir', os.path.dirname(os.path.abspath(__file__))),
                    ]
                    for label, search_dir in search_dirs:
                        potential = os.path.join(search_dir, clean_url)
                        print(f"   🔍 Checking {label}: {potential}")
                        if os.path.exists(potential):
                            file_path = potential
                            print(f"   ✅ Found in {label}!")
                            break
                    else:
                        print(f"   ⚠️ FILE NOT FOUND in any known location.")
        # --------------------------------------------------------
        
        # Generate interactions if not provided
        if not (frontend_interactions and len(frontend_interactions) > 0):
            print(f"📊 Generating deterministic interactions for video {video_id}")
            interactions = generate_deterministic_interactions(video_id, video_num)
        else:
            interactions = frontend_interactions
        
        # Run FULL PIPELINE (Behavioral + Media Forensics + Gemini)
        result = run_detection(
            file_path=file_path,
            interactions=interactions,
            post_id=f"reels_{video_id}",
            gemini_api_key=os.getenv('GEMINI_API_KEY')
        )
        
        # Add metadata
        result['video_id'] = video_id
        result['reel_metadata'] = {
            'username': reel_data.get('username'),
            'caption': reel_data.get('caption')
        }
        
        # Convert types
        result = convert_numpy_types(result)
        
        # Save to cache
        _ANALYSIS_CACHE[video_id] = result
        
        # No-cache headers
        response = jsonify(result)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def convert_numpy_types(obj):
    """Convert numpy types to Python native types"""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif hasattr(obj, 'item'):
        return obj.item()
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif pd.isna(obj):
        return None
    else:
        return obj

@app.route('/detect', methods=['POST'])
def detect():
    """
    Full detection pipeline:
      Accepts multipart/form-data (file upload) OR JSON body with media_url.

      JSON body fields:
        media_url    – URL of image/video to analyse
        post_id      – optional string identifier
        interactions – optional list of interaction dicts

      Form fields (multipart/form-data):
        file         – optional video/image upload
        interactions – optional JSON string of interaction list
        post_id      – optional string identifier
    """
    import traceback

    file_path = None
    tmp_path = None

    try:
        # ── Check for JSON body with media_url (from ASTRAVA Post analysis) ──
        json_body = None
        if request.is_json:
            json_body = request.json or {}

        if json_body and json_body.get('media_url'):
            media_url = json_body['media_url']
            print(f"📥 /detect received media_url: {media_url}")
            if media_url.startswith('http'):
                file_path = media_url  # VideoAIAnalyzer handles URL download
            else:
                file_path = media_url
        else:
            # ── Save uploaded file temporarily ────────────────────────────
            uploaded_file = request.files.get('media') or request.files.get('file')
            if uploaded_file and uploaded_file.filename:
                suffix = os.path.splitext(uploaded_file.filename)[-1] or '.tmp'
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp_path = tmp.name
                    uploaded_file.save(tmp_path)
                file_path = tmp_path
                print(f"📁 Saved upload to {file_path}")

        # ── Parse optional interactions ───────────────────────────────────
        interactions = []
        raw_interactions = None
        if json_body:
            raw_interactions = json_body.get('interactions')
        else:
            raw_interactions = request.form.get('interactions')

        if raw_interactions:
            if isinstance(raw_interactions, str):
                import json as _json
                interactions = _json.loads(raw_interactions)
            else:
                interactions = raw_interactions

        post_id = None
        if json_body:
            post_id = json_body.get('post_id')
        else:
            post_id = request.form.get('post_id')

        # ── Run pipeline ──────────────────────────────────────────────────
        result = run_detection(
            file_path=file_path,
            interactions=interactions,
            post_id=post_id,
            gemini_api_key=os.getenv('GEMINI_API_KEY'),
        )

        result = convert_numpy_types(result)
        return jsonify(result)

    except Exception as exc:
        print(f"❌ /detect error: {exc}")
        traceback.print_exc()
        return jsonify({'error': str(exc)}), 500

    finally:
        # Always clean up the temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
                print(f"🗑️  Removed temp file {tmp_path}")
            except Exception:
                pass


if __name__ == '__main__':
    # Clear cache on startup for fresh results
    _ANALYSIS_CACHE.clear()
    
    print("\n" + "="*60)
    print("🚀 ASTRAVA AI DETECTOR – Gemini Vision Powered")
    print("="*60)
    print("✅ 3-way fusion: Behavioral + Media Forensics + Gemini Vision")
    print("✅ Real media analysis via Gemini Vision API")
    print("✅ Serves ASTRAVA frontend on port 5173")
    print("✅ Backend running on port 5000")
    print("="*60)
    app.run(debug=True, port=5000, threaded=True)