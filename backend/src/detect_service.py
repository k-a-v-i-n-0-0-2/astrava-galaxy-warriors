"""
Detection Service — Orchestrates behavioral + media forensics pipeline.

Steps:
  1. Behavioral Analysis  (BehavioralFeatureExtractor)
  2. Media Forensics      (VideoAIAnalyzer)
  3. Gemini cross-check   (GeminiPostAnalyzer)
  4. Aggregate final confidence score
"""

import os
import uuid
import tempfile
import hashlib
import sys
import codecs
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Force UTF-8 encoding for standard output/error to prevent charmap errors on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import numpy as np
import pandas as pd

from .features import BehavioralFeatureExtractor
from .video_analyzer import VideoAIAnalyzer
from .gemini_analyzer import GeminiPostAnalyzer


# ─── helpers ──────────────────────────────────────────────────────────────────

def _build_synthetic_interactions(post_id: str, n: int = 20) -> pd.DataFrame:
    """
    Build a small synthetic interaction DataFrame when no real interactions are
    available (needed so behavioral analysis always has data to work with).
    """
    seed = int(hashlib.md5(str(post_id).encode()).hexdigest()[:8], 16)
    rng = np.random.RandomState(seed)
    base = datetime.now() - timedelta(hours=1)
    rows = []
    for i in range(n):
        rows.append({
            "user_id": f"user_{rng.randint(1, 100):03d}",
            "timestamp": (base + timedelta(minutes=rng.uniform(0, 60))).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "action_type": rng.choice(["like", "comment", "share", "repost"]),
            "post_id": post_id,
        })
    return pd.DataFrame(rows)


def _behavioral_score(features: Dict) -> float:
    """
    Convert extracted features into a 0-100 'AI-likeness' score.
    Returns higher values for bot-like patterns.
    """
    score = 0.0

    # Spread speed: fast spread → higher score
    ss = features.get("spread_speed", {})
    if ss.get("is_abnormal"):
        score += 20

    # Early burst
    eb = features.get("early_burst", {})
    if eb.get("is_abnormal"):
        score += 20

    # Synchronisation
    sy = features.get("synchronization", {})
    if sy.get("is_abnormal"):
        score += 20

    # User diversity: low diversity → higher score
    ud = features.get("user_diversity", {})
    if ud.get("is_abnormal"):
        score += 20

    # Entropy: low entropy → suspicious
    be = features.get("behavioral_entropy", {})
    if be.get("is_abnormal"):
        score += 20

    return min(score, 100.0)


def _media_score(media_result: Optional[Dict]) -> float:
    """Return 0-100 AI probability from video analyzer result (or 0 if absent)."""
    if not media_result:
        return 0.0
    return float(media_result.get("ai_probability", 0))


def _weighted_confidence(behavioral: float, media: float, has_media: bool) -> float:
    """
    Combine behavioral + media scores into a final confidence score.
    If no media was uploaded the behavioral score carries full weight.
    """
    if has_media:
        # Boost accuracy by weighting the highest anomaly signal more heavily
        highest_signal = max(behavioral, media)
        secondary_signal = min(behavioral, media)
        combined = highest_signal + (secondary_signal * 0.4)
        return min(combined, 98.5)
    
    return min(behavioral * 1.2, 98.5)


# ─── public API ───────────────────────────────────────────────────────────────

def run_detection(
    file_path: Optional[str] = None,
    interactions: Optional[list] = None,
    post_id: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Main detection pipeline.

    Parameters
    ----------
    file_path       : Absolute path to uploaded video/image (may be None).
    interactions    : List of interaction dicts from the frontend (may be None/empty).
    post_id         : Identifier for the post being analysed.
    gemini_api_key  : Gemini API key (falls back to GEMINI_API_KEY env var).

    Returns
    -------
    dict with keys:
        confidence          – 0-100 final AI-likelihood score
        label               – human-readable verdict
        behavioral_score    – 0-100 score from behavioral analysis
        media_score         – 0-100 score from media forensics (0 if no file)
        behavioral_signals  – dict of individual behavioral feature results
        media_signals       – dict from VideoAIAnalyzer (or None)
        triggered_patterns  – list of human-readable triggered signals
        gemini_insights     – dict from Gemini (or None)
        timestamp           – ISO-formatted analysis timestamp
    """
    post_id = post_id or str(uuid.uuid4())
    
    # Check if media exists locally, OR if it's an HTTP URL (which VideoAIAnalyzer downloads)
    has_media = False
    if file_path:
        file_path_str = str(file_path)
        if file_path_str.startswith('http://') or file_path_str.startswith('https://'):
            has_media = True
        elif os.path.exists(file_path):
            has_media = True
            
    triggered_patterns: list = []

    # ── 1. Behavioral analysis ──────────────────────────────────────────────
    print(f"\n[DetectService] Step 1 – Behavioral Analysis for post {post_id}")
    extractor = BehavioralFeatureExtractor()

    if interactions and len(interactions) > 0:
        df = pd.DataFrame(interactions)
        df["post_id"] = post_id
    else:
        print("  ⚠️  No interactions provided — using synthetic sample")
        df = _build_synthetic_interactions(post_id)

    behavioral_features = extractor.extract_all_features(post_id, df)
    b_score = _behavioral_score(behavioral_features)

    # Collect triggered behavioral signal labels
    for name, result in behavioral_features.items():
        if isinstance(result, dict) and result.get("is_abnormal"):
            triggered_patterns.append(f"Behavioral: {name.replace('_', ' ').title()} anomaly detected")

    print(f"  ✅ Behavioral score: {b_score:.1f}%")

    # ── 2. Media forensics ──────────────────────────────────────────────────
    media_result = None
    m_score = 0.0

    if has_media:
        print(f"\n[DetectService] Step 2 – Media Forensics on {file_path}")
        try:
            analyzer = VideoAIAnalyzer()
            media_result = analyzer.analyze_video(file_path)
            m_score = _media_score(media_result)
            triggered_patterns.extend(media_result.get("triggered_patterns", []))
            print(f"  ✅ Media score: {m_score:.1f}%")
        except Exception as exc:
            print(f"  ⚠️  Media analysis failed: {exc}")
            media_result = {"error": str(exc)}
    else:
        print("\n[DetectService] Step 2 – No media file uploaded, skipping media forensics")

    # ── 3. Aggregate score ──────────────────────────────────────────────────
    confidence = round(_weighted_confidence(b_score, m_score, has_media), 1)

    if confidence >= 85:
        label = "AI-Generated · High Confidence"
    elif confidence >= 70:
        label = "Likely AI-Generated · Medium Confidence"
    elif confidence >= 50:
        label = "Possibly AI-Generated · Low Confidence"
    else:
        label = "Likely Human Content"

    print(f"\n[DetectService] Step 3 – Final confidence: {confidence}%  →  {label}")

    # ── 4. Gemini cross-check ───────────────────────────────────────────────
    gemini_insights = None
    try:
        print("\n[DetectService] Step 4 – Gemini cross-check")
        gemini = GeminiPostAnalyzer(api_key=gemini_api_key or os.getenv("GEMINI_API_KEY"))
        if gemini.is_available:
            gemini_insights = gemini.generate_post_insights({
                "post_id": post_id,
                "confidence": confidence,
                "triggered_signals": triggered_patterns,
            })
            print(f"  ✅ Gemini insights: {gemini_insights.get('summary', '')[:80]}")
        else:
            print("  ⚠️  Gemini not available – skipping")
    except Exception as exc:
        print(f"  ⚠️  Gemini step failed: {exc}")

    # ── 5. Unify signals for frontend ───────────────────────────────────────
    all_signals = {}
    
    # Behavioral signals (already 0-100 likelihood)
    for k, v in behavioral_features.items():
        if isinstance(v, dict):
            all_signals[f"behavioral_{k}"] = v.get("score", 50.0)
        else:
            all_signals[f"behavioral_{k}"] = float(v)

    # Media signals
    if media_result and "signals" in media_result:
        for k, v in media_result["signals"].items():
            all_signals[f"forensic_{k}"] = v

    return {
        "confidence": confidence,
        "label": label,
        "behavioral_score": round(b_score, 1),
        "media_score": round(m_score, 1),
        "behavioral_signals": behavioral_features,
        "media_signals": media_result,
        "signals": all_signals,  # Unified signals for accuracy display
        "triggered_patterns": triggered_patterns,
        "gemini_insights": gemini_insights,
        "timestamp": datetime.now().isoformat(),
    }
