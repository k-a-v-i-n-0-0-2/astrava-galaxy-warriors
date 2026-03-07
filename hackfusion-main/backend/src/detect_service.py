"""
Detection Service — Full Local ML-Powered Pipeline.

Pipeline:
  Video -> Extract Frames -> 8 Forensic Checks -> ML Classifier -> Final Score
                                                       |
                                          Gemini Vision (optional bonus)

ML classifier is 100% of the score when Gemini is unavailable.
When Gemini works: ML 75% + Gemini 25%.
Behavioral analysis only used with real interactions (never synthetic).
"""

import os
import sys
import uuid
import hashlib
import codecs
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Force UTF-8 for Windows terminal
if sys.stdout and hasattr(sys.stdout, 'encoding') and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    except:
        pass
if sys.stderr and hasattr(sys.stderr, 'encoding') and sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')
    except:
        pass

import numpy as np
import pandas as pd

from .features import BehavioralFeatureExtractor
from .video_analyzer import VideoAIAnalyzer
from .ml_classifier import get_classifier


def _log(msg: str):
    print(msg, flush=True)


# ── helpers ───────────────────────────────────────────────────────────────────

def _build_synthetic_interactions(post_id: str, n: int = 20) -> pd.DataFrame:
    seed = int(hashlib.md5(str(post_id).encode()).hexdigest()[:8], 16)
    rng = np.random.RandomState(seed)
    base = datetime.now() - timedelta(hours=1)
    rows = []
    for i in range(n):
        rows.append({
            "user_id": f"user_{rng.randint(1, 100):03d}",
            "timestamp": (base + timedelta(minutes=rng.uniform(0, 60))).strftime("%Y-%m-%d %H:%M:%S"),
            "action_type": rng.choice(["like", "comment", "share", "repost"]),
            "post_id": post_id,
        })
    return pd.DataFrame(rows)


def _behavioral_score(features: Dict) -> float:
    """Compute a graduated behavioral anomaly score based on actual metrics."""
    score = 0.0
    weights = {
        "spread_speed": 25,
        "early_burst": 20,
        "synchronization": 20,
        "user_diversity": 15,
        "behavioral_entropy": 20,
    }
    for key, max_pts in weights.items():
        sub = features.get(key, {})
        if isinstance(sub, dict):
            if sub.get("is_abnormal"):
                # Graduated: stronger anomaly value → more points
                val = sub.get("value", 0)
                if key == "spread_speed":
                    # Faster spread → higher score (val is avg gap in seconds)
                    intensity = max(0, min(1, (60 - val) / 60)) if val < 60 else 0
                elif key == "early_burst":
                    # Higher burst ratio → higher score
                    intensity = max(0, min(1, val / 1.0))
                elif key == "synchronization":
                    intensity = max(0, min(1, val / 1.0))
                elif key == "user_diversity":
                    # Lower diversity → higher score
                    intensity = max(0, min(1, (0.5 - val) / 0.5)) if val < 0.5 else 0
                elif key == "behavioral_entropy":
                    # Lower entropy → higher score
                    intensity = max(0, min(1, (2.5 - val) / 2.5)) if val < 2.5 else 0
                else:
                    intensity = 0.7  # default for unknown keys
                score += max_pts * max(0.5, intensity)  # At least 50% if flagged
    return min(score, 100.0)


# ── main pipeline ─────────────────────────────────────────────────────────────

def run_detection(
    file_path: Optional[str] = None,
    interactions: Optional[list] = None,
    post_id: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Main detection pipeline. Returns confidence 0-100 and detailed signals.
    """
    post_id = post_id or str(uuid.uuid4())
    has_real_interactions = bool(interactions and len(interactions) > 0)

    # Check media availability
    has_media = False
    if file_path:
        fp = str(file_path)
        if fp.startswith('http://') or fp.startswith('https://'):
            has_media = True
        elif os.path.exists(file_path):
            has_media = True

    triggered_patterns: list = []

    _log(f"\n{'='*60}")
    _log(f"  ASTRAVA DETECTION PIPELINE - {post_id}")
    _log(f"  Media: {'YES ' + str(file_path)[:60] if has_media else 'NO media'}")
    _log(f"  Real interactions: {'YES' if has_real_interactions else 'NO (synthetic)'}")
    _log(f"{'='*60}")

    # ── 1. Behavioral analysis ────────────────────────────────────────────
    _log(f"\n  [1/4] Behavioral Analysis")
    extractor = BehavioralFeatureExtractor()

    if has_real_interactions:
        df = pd.DataFrame(interactions)
        df["post_id"] = post_id
        _log(f"      Using {len(interactions)} real interactions")
    else:
        _log(f"      No real interactions - synthetic (weight=0%)")
        df = _build_synthetic_interactions(post_id)

    behavioral_features = extractor.extract_all_features(post_id, df)
    b_score = _behavioral_score(behavioral_features)

    for name, result in behavioral_features.items():
        if isinstance(result, dict) and result.get("is_abnormal"):
            triggered_patterns.append(f"Behavioral: {name.replace('_', ' ').title()} anomaly")

    _log(f"      Behavioral score: {b_score:.1f}% {'(IGNORED)' if not has_real_interactions else ''}")

    # ── 2. Media forensics (8 checks) ────────────────────────────────────
    media_result = None
    m_score = 0.0
    feature_vector = None

    if has_media:
        _log(f"\n  [2/4] Media Forensics (8 checks)")
        try:
            analyzer = VideoAIAnalyzer()
            media_result = analyzer.analyze_video(file_path)
            m_score = float(media_result.get("ai_probability", 0))
            feature_vector = media_result.get("feature_vector")
            triggered_patterns.extend(media_result.get("triggered_patterns", []))
            _log(f"      Media forensics score: {m_score:.1f}%")
        except Exception as exc:
            _log(f"      Media analysis failed: {exc}")
            import traceback
            traceback.print_exc()
            media_result = {"error": str(exc)}
    else:
        _log(f"\n  [2/4] Skipped (no media)")

    # ── 3. ML Classifier ─────────────────────────────────────────────────
    ml_result = None
    ml_score = 0.0
    has_ml = False

    if feature_vector and len(feature_vector) == 11:
        _log(f"\n  [3/4] ML Classifier (RandomForest + Forensics Blend)")
        try:
            classifier = get_classifier()
            ml_result = classifier.predict(feature_vector, forensic_score=m_score)
            ml_score = ml_result['ai_probability']
            has_ml = True
            _log(f"      ML ensemble score: {ml_score:.1f}%")
            _log(f"      RF: {ml_result['rf_probability']:.1f}% | Forensic: {m_score:.1f}%")
        except Exception as exc:
            _log(f"      ML classifier failed: {exc}")
            import traceback
            traceback.print_exc()
    else:
        _log(f"\n  [3/4] ML Classifier - Skipped (no feature vector)")

    # ── 4. Gemini Vision (optional bonus) ─────────────────────────────────
    gemini_score = 0.0
    has_gemini = False
    gemini_vision_result = None

    _log(f"\n  [4/4] Gemini Vision (optional)")
    try:
        from .gemini_analyzer import GeminiPostAnalyzer
        gemini = GeminiPostAnalyzer(api_key=gemini_api_key or os.getenv("GEMINI_API_KEY"))
        if gemini.is_available and has_media and file_path:
            _log(f"      Sending to Gemini...")
            gemini_vision_result = gemini.analyze_media_content(file_path)
            if gemini_vision_result and gemini_vision_result.get('ai_score') is not None:
                gemini_score = gemini_vision_result['ai_score'] * 100
                has_gemini = True
                _log(f"      Gemini score: {gemini_score:.1f}%")
            else:
                reason = gemini_vision_result.get('details', 'Unknown') if gemini_vision_result else 'No result'
                _log(f"      Gemini returned no score: {reason}")
        elif not gemini.is_available:
            _log(f"      Gemini unavailable (API key issue) - using local ML only")
        else:
            _log(f"      Skipped (no media)")
    except Exception as exc:
        _log(f"      Gemini failed: {exc} - continuing with local ML")

    # ── FINAL SCORE ──────────────────────────────────────────────────────
    _log(f"\n  [SCORING] Final confidence calculation")

    if has_ml:
        if has_gemini:
            # ML 75% + Gemini 25%
            confidence = ml_score * 0.75 + gemini_score * 0.25
            _log(f"      Mode: ML 75% + Gemini 25%")

            # Max-dominance
            if gemini_score > 85:
                confidence = max(confidence, gemini_score * 0.9)
                _log(f"      Max-Dominance: Gemini {gemini_score:.1f}%")
        else:
            # ML 100%
            confidence = ml_score
            _log(f"      Mode: ML 100% (Gemini unavailable)")

        # Behavioral bonus if real interactions
        if has_real_interactions and b_score > 60:
            confidence = confidence * 0.85 + b_score * 0.15
            _log(f"      +Behavioral adjustment: {b_score:.1f}%")

    elif has_media and m_score > 0:
        # Fallback to raw forensics score
        confidence = m_score
        _log(f"      Mode: Raw forensics 100% (ML unavailable)")
    else:
        confidence = b_score if has_real_interactions else 0.0
        _log(f"      Mode: {'Behavioral only' if has_real_interactions else 'No data'}")

    confidence = round(min(99.0, max(0.0, confidence)), 1)

    if confidence >= 80:
        label = "AI-Generated - High Confidence"
    elif confidence >= 60:
        label = "Likely AI-Generated - Medium Confidence"
    elif confidence >= 40:
        label = "Possibly AI-Generated - Low Confidence"
    elif confidence >= 20:
        label = "Uncertain - Insufficient Evidence"
    else:
        label = "Likely Human Content"

    _log(f"\n{'='*60}")
    _log(f"  RESULT: {confidence}% -> {label}")
    _log(f"  Behavioral: {b_score:.1f}% {'(IGNORED)' if not has_real_interactions else ''}")
    _log(f"  Media Forensics: {m_score:.1f}%")
    _log(f"  ML Classifier: {ml_score:.1f}% {'OK' if has_ml else 'N/A'}")
    _log(f"  Gemini Vision: {gemini_score:.1f}% {'OK' if has_gemini else 'UNAVAILABLE'}")
    _log(f"{'='*60}\n")

    # ── Build response ───────────────────────────────────────────────────
    all_signals = {}

    # Behavioral signals only if real
    if has_real_interactions:
        for k, v in behavioral_features.items():
            if isinstance(v, dict):
                all_signals[f"behavioral_{k}"] = v.get("score", 50.0)
            else:
                all_signals[f"behavioral_{k}"] = float(v)

    # Media forensic signals
    if media_result and "signals" in media_result and isinstance(media_result["signals"], dict):
        for k, v in media_result["signals"].items():
            all_signals[f"forensic_{k}"] = v

    # Gemini signals
    if has_gemini and gemini_vision_result and 'signals' in gemini_vision_result:
        for k, v in gemini_vision_result['signals'].items():
            all_signals[f"gemini_{k}"] = v

    # Gemini insights
    gemini_insights = None
    if gemini_vision_result and 'ai_score' in gemini_vision_result:
        gemini_insights = {
            'summary': gemini_vision_result.get('details', ''),
            'ai_score': gemini_vision_result.get('ai_score'),
            'confidence_level': gemini_vision_result.get('confidence_level'),
            'details': gemini_vision_result.get('details'),
        }

    return {
        "confidence": confidence,
        "label": label,
        "behavioral_score": round(b_score, 1),
        "media_score": round(m_score, 1),
        "ml_score": round(ml_score, 1) if has_ml else None,
        "gemini_score": round(gemini_score, 1) if has_gemini else None,
        "ml_result": ml_result,
        "behavioral_signals": behavioral_features if has_real_interactions else {},
        "media_signals": media_result,
        "signals": all_signals,
        "triggered_patterns": triggered_patterns,
        "gemini_insights": gemini_insights,
        "timestamp": datetime.now().isoformat(),
    }
