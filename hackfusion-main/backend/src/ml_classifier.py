"""
ML Classifier for AI Content Detection — Scikit-learn based.

Uses Random Forest + Isolation Forest ensemble trained on reference signal patterns.

Feature vector (11 dimensions):
  [facial_consistency, expression_symmetry, lip_sync, gan_noise,
   texture_regularity, color_anomaly, temporal_coherence, edge_artifacts,
   watermark_artifacts, ela_analysis, metadata_forensics]

Each feature is a 0-100 anomaly score from VideoAIAnalyzer.
When no faces are detected, facial/symmetry/lip_sync return ~15% (low = real).
Checks that fail or find no evidence return 0% (not 50%).
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler

def _log(msg: str):
    print(msg, flush=True)


# ── Reference Training Data ──────────────────────────────────────────────────
# 11-feature vectors:
#   [facial, symmetry, lip_sync, gan_noise, texture, color,
#    temporal, edge, watermark, ela, metadata]
#
# Calibrated to match forensic check outputs:
#   - No-face videos: facial=15, symmetry=15, lip_sync=15
#   - Checks that fail/no-evidence: 0
#   - Real videos: low scores on most checks
#   - AI videos: elevated on characteristic signals

# AI-GENERATED patterns (label=1)
_AI_PATTERNS = np.array([
    # Deepfake face-swap (has faces: high facial, symmetry, lip-sync)
    [75, 70, 72, 40, 55, 45, 65, 58, 30, 45, 35],
    [82, 65, 78, 35, 50, 40, 70, 62, 35, 50, 40],
    [68, 75, 65, 38, 52, 48, 60, 55, 28, 42, 32],
    [90, 60, 85, 30, 45, 35, 75, 68, 40, 55, 45],
    [78, 72, 70, 42, 58, 50, 68, 60, 32, 48, 38],
    # GAN-generated video (no real faces, high GAN noise + texture)
    [15, 15, 15, 65, 78, 72, 80, 65, 55, 60, 50],
    [15, 15, 15, 70, 82, 68, 85, 70, 60, 65, 55],
    [15, 15, 15, 60, 75, 65, 75, 62, 50, 55, 45],
    [15, 15, 15, 68, 80, 70, 82, 68, 58, 62, 52],
    [15, 15, 15, 55, 72, 62, 78, 60, 48, 52, 42],
    # Diffusion model (no faces, smooth textures, high temporal)
    [15, 15, 15, 45, 85, 75, 90, 78, 45, 70, 55],
    [15, 15, 15, 40, 82, 80, 88, 75, 42, 68, 52],
    [15, 15, 15, 50, 88, 72, 92, 82, 50, 72, 58],
    [15, 15, 15, 42, 80, 78, 85, 76, 40, 65, 50],
    [15, 15, 15, 48, 90, 70, 95, 80, 48, 75, 60],
    # Sora/video-gen (no faces, high temporal coherence)
    [15, 15, 15, 35, 70, 55, 90, 62, 38, 55, 42],
    [15, 15, 15, 30, 68, 52, 92, 58, 35, 52, 40],
    [15, 15, 15, 40, 72, 58, 88, 65, 42, 58, 45],
    [15, 15, 15, 32, 65, 48, 95, 55, 35, 50, 38],
    [15, 15, 15, 38, 75, 60, 85, 68, 40, 60, 48],
    # AI with some face detection (moderate facial + high others)
    [45, 50, 40, 55, 72, 68, 70, 65, 35, 50, 40],
    [50, 55, 45, 50, 78, 72, 75, 70, 40, 55, 45],
    [40, 48, 35, 60, 80, 70, 68, 72, 38, 58, 48],
    [55, 52, 50, 45, 70, 65, 72, 68, 32, 48, 38],
    [48, 58, 42, 52, 75, 68, 78, 65, 36, 52, 42],
    # AI with high temporal coherence (key AI signal)
    [15, 15, 15, 30, 50, 40, 85, 45, 30, 40, 30],
    [15, 15, 15, 25, 45, 35, 90, 40, 28, 38, 28],
    [15, 15, 15, 35, 55, 45, 80, 50, 35, 45, 35],
    [15, 15, 15, 28, 48, 38, 88, 42, 30, 40, 30],
    [15, 15, 15, 32, 52, 42, 82, 48, 32, 42, 32],
    # Modern AI video generators (clean look, high temporal + moderate GAN)
    [15, 15, 15, 30, 10, 0, 64, 3, 25, 35, 20],
    [15, 15, 15, 28, 12, 5, 60, 5, 22, 32, 18],
    [15, 15, 15, 35, 8, 2, 68, 4, 28, 38, 22],
    [15, 15, 15, 32, 15, 8, 62, 6, 25, 35, 20],
    [15, 15, 15, 25, 5, 0, 70, 2, 20, 30, 15],
    [15, 15, 15, 38, 18, 10, 58, 8, 30, 40, 25],
    [15, 15, 15, 40, 20, 12, 55, 10, 32, 42, 28],
    [15, 15, 15, 22, 8, 3, 72, 5, 18, 28, 14],
    # AI with strong watermark/ELA signals
    [15, 15, 15, 40, 50, 30, 60, 20, 65, 70, 55],
    [15, 15, 15, 35, 45, 25, 55, 15, 70, 75, 60],
    [15, 15, 15, 42, 55, 35, 65, 25, 60, 65, 50],
])

# HUMAN/REAL patterns (label=0)
_HUMAN_PATTERNS = np.array([
    # Clean real video, no faces (typical phone video)
    [15, 15, 15, 10, 5, 8, 20, 5, 5, 5, 8],
    [15, 15, 15, 15, 8, 12, 25, 8, 8, 8, 10],
    [15, 15, 15, 12, 3, 10, 18, 3, 3, 3, 5],
    [15, 15, 15, 8, 2, 5, 15, 2, 2, 2, 4],
    [15, 15, 15, 18, 10, 15, 30, 10, 10, 10, 12],
    # Real video with faces (natural asymmetry, low scores)
    [25, 20, 22, 12, 8, 10, 22, 8, 5, 8, 10],
    [30, 28, 25, 15, 10, 12, 28, 10, 8, 10, 12],
    [22, 18, 20, 10, 5, 8, 18, 5, 3, 5, 8],
    [28, 25, 22, 18, 12, 15, 25, 12, 10, 12, 14],
    [20, 22, 18, 14, 8, 10, 20, 8, 5, 8, 10],
    # Slightly noisy real video (phone, compression)
    [15, 15, 15, 25, 12, 18, 35, 20, 12, 15, 18],
    [15, 15, 15, 30, 15, 20, 38, 25, 15, 18, 20],
    [15, 15, 15, 22, 10, 15, 32, 18, 10, 12, 15],
    [15, 15, 15, 28, 18, 22, 40, 22, 15, 18, 22],
    [15, 15, 15, 20, 8, 12, 28, 15, 8, 10, 12],
    # Real with compression artifacts (heavy JPEG/web)
    [15, 15, 15, 20, 8, 10, 25, 35, 10, 15, 12],
    [15, 15, 15, 25, 10, 12, 20, 40, 12, 18, 14],
    [15, 15, 15, 18, 5, 8, 22, 38, 8, 12, 10],
    [15, 15, 15, 22, 12, 15, 28, 42, 14, 20, 16],
    [15, 15, 15, 15, 3, 5, 18, 30, 5, 8, 8],
    # Real with faces + motion (natural)
    [20, 18, 15, 10, 5, 8, 30, 8, 5, 5, 8],
    [25, 22, 20, 12, 8, 10, 35, 10, 8, 8, 10],
    [18, 15, 12, 15, 10, 12, 28, 12, 8, 10, 12],
    [22, 20, 18, 8, 3, 5, 25, 5, 3, 3, 5],
    [28, 25, 22, 14, 8, 10, 32, 8, 8, 8, 10],
    # Real outdoor/action video (moderate temporal from real motion)
    [15, 15, 15, 18, 5, 10, 42, 8, 5, 8, 10],
    [15, 15, 15, 22, 8, 12, 45, 10, 8, 10, 12],
    [15, 15, 15, 15, 3, 8, 38, 5, 3, 5, 8],
    [15, 15, 15, 20, 10, 15, 40, 12, 10, 12, 14],
    [15, 5, 15, 30, 1, 0, 23, 1, 2, 3, 5],
    # Real with some ELA noise (JPEG artifacts)
    [15, 15, 15, 12, 5, 8, 20, 30, 8, 25, 10],
    [15, 15, 15, 15, 8, 10, 22, 35, 10, 28, 12],
])


class DeepfakeMLClassifier:
    """
    Ensemble classifier: Random Forest (supervised) + forensic score blending.
    RF trained on reference patterns matching the calibrated forensic output ranges.
    Now uses 11-dimensional feature vectors.
    """

    def __init__(self):
        self.rf = None
        self.scaler = StandardScaler()
        self._trained = False
        self._train()

    def _train(self):
        """Train on embedded reference dataset."""
        _log("      [ML] Training classifier on reference patterns...")

        X_ai = _AI_PATTERNS
        X_human = _HUMAN_PATTERNS

        # Add noise augmentation for robustness
        rng = np.random.RandomState(42)
        X_ai_aug = np.vstack([X_ai + rng.uniform(-3, 3, X_ai.shape) for _ in range(3)])
        X_human_aug = np.vstack([X_human + rng.uniform(-3, 3, X_human.shape) for _ in range(3)])
        X_ai_aug = np.clip(X_ai_aug, 0, 100)
        X_human_aug = np.clip(X_human_aug, 0, 100)

        X = np.vstack([X_ai, X_ai_aug, X_human, X_human_aug])
        y = np.concatenate([
            np.ones(len(X_ai) + len(X_ai_aug)),
            np.zeros(len(X_human) + len(X_human_aug))
        ])

        # Fit scaler
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)

        # Random Forest — the primary classifier
        self.rf = RandomForestClassifier(
            n_estimators=150,
            max_depth=10,
            min_samples_split=3,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'
        )
        self.rf.fit(X_scaled, y)

        self._trained = True
        _log(f"      [ML] Trained on {len(X)} samples ({len(X_ai)+len(X_ai_aug)} AI, {len(X_human)+len(X_human_aug)} Human)")

    def predict(self, feature_vector: list, forensic_score: float = None) -> dict:
        """
        Predict AI probability from forensic feature vector.
        
        Args:
            feature_vector: 11-element list of 0-100 anomaly scores
            forensic_score: Optional raw forensic weighted score (0-100)
        
        Returns dict with ai_probability, confidence, etc.
        """
        if not self._trained:
            self._train()

        X = np.array(feature_vector).reshape(1, -1)
        X_scaled = self.scaler.transform(X)

        # Random Forest probability
        rf_proba = self.rf.predict_proba(X_scaled)[0]
        rf_ai_prob = rf_proba[1] * 100

        # Feature importance from RF
        importances = self.rf.feature_importances_
        feature_names = [
            'facial_consistency', 'expression_symmetry', 'lip_sync', 'gan_noise',
            'texture_regularity', 'color_anomaly', 'temporal_coherence', 'edge_artifacts',
            'watermark_artifacts', 'ela_analysis', 'metadata_forensics'
        ]

        # Key signal analysis: check if strong individual signals exist
        fv = np.array(feature_vector)
        temporal = fv[6]    # temporal_coherence
        gan = fv[3]         # gan_noise
        texture = fv[4]     # texture_regularity
        watermark = fv[8]   # watermark_artifacts
        ela = fv[9]         # ela_analysis
        metadata = fv[10]   # metadata_forensics

        # Key differentiators: temporal, texture, gan, plus new signals
        key_signals = [texture, temporal, gan, watermark, ela, metadata]
        max_key_signal = max(key_signals)

        # Ensemble: RF result + forensic score boost for high-signal cases
        ensemble_prob = rf_ai_prob

        # If forensic score available, blend with RF
        if forensic_score is not None:
            # RF 60% + Forensic 40%  
            ensemble_prob = rf_ai_prob * 0.60 + forensic_score * 0.40
            
            # If any key signal is very high (>75%), boost the score
            if max_key_signal > 75:
                boost = min(20, (max_key_signal - 75) * 0.8)
                ensemble_prob = min(99, ensemble_prob + boost)

        # Temporal coherence is one of the strongest AI indicators.
        # Modern AI video generators produce clean textures/colors but
        # always exhibit unnatural temporal patterns (frame-to-frame flow).
        # If temporal >= 55 AND gan_noise >= 25, this is a strong AI signal.
        if temporal >= 55 and gan >= 25:
            temporal_boost = (temporal - 40) * 0.6 + (gan - 15) * 0.3
            ensemble_prob = max(ensemble_prob, temporal_boost)
            _log(f"      [ML] Temporal+GAN boost applied: {temporal_boost:.1f}%")

        # ELA + watermark cross-validation: if both are elevated, strong AI signal
        if ela >= 40 and watermark >= 35:
            cross_boost = (ela - 30) * 0.4 + (watermark - 25) * 0.3
            ensemble_prob = max(ensemble_prob, cross_boost)
            _log(f"      [ML] ELA+Watermark cross-validation boost: {cross_boost:.1f}%")

        # Confidence based on RF probability margin + signal count
        rf_margin = abs(rf_proba[1] - rf_proba[0])
        # Count how many signals are elevated (> 30%)
        elevated_count = sum(1 for s in fv if s > 30)
        # More elevated signals = more evidence = higher confidence
        evidence_factor = min(20, elevated_count * 3)
        confidence = max(35, min(98, rf_margin * 80 + evidence_factor))

        _log(f"      [ML] RF: {rf_ai_prob:.1f}% | Forensic: {forensic_score:.1f}% | Ensemble: {ensemble_prob:.1f}%")
        _log(f"      [ML] Top features: {', '.join(f'{feature_names[i]}={importances[i]:.2f}' for i in np.argsort(importances)[::-1][:4])}")

        return {
            'ai_probability': round(min(99, max(0, ensemble_prob)), 1),
            'confidence': round(confidence, 1),
            'rf_probability': round(rf_ai_prob, 1),
            'forensic_score': round(forensic_score, 1) if forensic_score is not None else None,
            'feature_importances': {feature_names[i]: round(float(importances[i]), 3) for i in range(len(feature_names))},
            'method': 'RandomForest(60%) + Forensics(40%) + CrossValidation ensemble',
        }


# Singleton
_classifier = None

def get_classifier() -> DeepfakeMLClassifier:
    global _classifier
    if _classifier is None:
        _classifier = DeepfakeMLClassifier()
    return _classifier
