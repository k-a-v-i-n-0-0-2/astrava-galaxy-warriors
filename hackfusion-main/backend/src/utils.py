"""
Utility functions and thresholds for Instagram AI Confidence Labeler.
"""

from dataclasses import dataclass
from typing import Dict

@dataclass
class DetectionThresholds:
    SPREAD_SPEED_THRESHOLD_SECONDS: float = 60.0
    EARLY_BURST_THRESHOLD_PERCENT: float = 0.40
    SYNC_WINDOW_SECONDS: int = 2
    SYNC_THRESHOLD_PERCENT: float = 0.30
    USER_DIVERSITY_THRESHOLD: float = 0.50
    ENTROPY_THRESHOLD: float = 2.5
    GRAPH_CLUSTERING_THRESHOLD: float = 0.30

def calculate_confidence_score(abnormal_count: int) -> int:
    """Calculate confidence score based on number of abnormal signals."""
    if abnormal_count >= 5:
        return 92
    elif abnormal_count >= 4:
        return 85
    elif abnormal_count >= 3:
        return 78
    elif abnormal_count >= 2:
        return 55
    elif abnormal_count >= 1:
        return 35
    return 0

def format_instagram_ui_label(confidence: int) -> str:
    """Format confidence score as Instagram UI text."""
    if confidence >= 85:
        return "AI-generated  High confidence"
    elif confidence >= 70:
        return "AI-generated  Medium confidence"
    elif confidence >= 50:
        return "AI-generated  Low confidence"
    return ""

def get_instagram_tap_detail(confidence: int) -> str:
    """Generate tap-for-details explanation text."""
    if confidence >= 85:
        return "This post shows strong patterns associated with AI-generated content."
    elif confidence >= 70:
        return "This post shows clear patterns commonly associated with AI-generated content."
    elif confidence >= 50:
        return "This post shows some patterns associated with AI-generated content."
    return "Content appears to be spreading organically."

def get_signal_descriptions() -> Dict[str, str]:
    """Human-readable descriptions of each behavioral signal."""
    return {
        "spread_speed": "Abnormally fast and consistent interaction timing",
        "early_burst": "Concentrated interactions immediately after posting",
        "synchronization": "Multiple users acting within 2-second windows",
        "user_diversity": "Low ratio of unique users to total interactions",
        "behavioral_entropy": "Low randomness in interaction timing patterns",
        "graph_clustering": "Densely connected user interaction network"
    }
