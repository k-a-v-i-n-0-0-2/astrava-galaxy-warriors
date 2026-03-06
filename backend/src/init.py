"""Coordinated Amplification Detection System - Internal Platform Signal.

This package provides backend behavioral analysis for detecting artificially
coordinated content amplification across social media platforms.
"""

from .loader import InteractionDataLoader
from .features import BehavioralFeatureExtractor
from .entropy import BehavioralEntropyAnalyzer
from .graph_analysis import InteractionGraphAnalyzer
from .detector import CoordinatedAmplificationDetector
from .utils import DetectionThresholds

__version__ = "1.0.0"
__all__ = [
    'InteractionDataLoader',
    'BehavioralFeatureExtractor',
    'BehavioralEntropyAnalyzer',
    'InteractionGraphAnalyzer',
    'CoordinatedAmplificationDetector',
    'DetectionThresholds'
]
