"""Core detection logic with Gemini API integration."""

import pandas as pd
from typing import Dict, List, Any, Optional

from .features import BehavioralFeatureExtractor
from .graph_analysis import InteractionGraphAnalyzer
from .gemini_analyzer import GeminiPostAnalyzer
from .utils import DetectionThresholds, calculate_confidence_score, format_instagram_ui_label, get_instagram_tap_detail, get_signal_descriptions

class InstagramAIConfidenceLabeler:
    """
    Analyzes YOUR post data and returns confidence labels.
    Now with Gemini API for enhanced insights!
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize the labeler.
        
        Args:
            gemini_api_key: Optional Gemini API key for enhanced analysis
        """
        self.feature_extractor = BehavioralFeatureExtractor()
        self.graph_analyzer = InteractionGraphAnalyzer()
        self.thresholds = DetectionThresholds()
        self.signal_descriptions = get_signal_descriptions()
        
        # Initialize Gemini if API key provided
        self.gemini = GeminiPostAnalyzer(api_key=gemini_api_key)
    
    def analyze_post(self, post_id: str, interactions_df: pd.DataFrame, use_gemini: bool = True) -> Dict[str, Any]:
        """
        Analyze a post and return complete results with optional Gemini insights.
        
        Args:
            post_id: Your post/video ID
            interactions_df: DataFrame with interaction data
            use_gemini: Whether to enhance analysis with Gemini API
        
        Returns:
            Dictionary with analysis results and optional Gemini insights
        """
        
        # Check for minimum data
        if len(interactions_df) < 3:
            return self._insufficient_data_response(post_id, interactions_df)
        
        # Extract all behavioral features
        behavioral_features = self.feature_extractor.extract_all_features(post_id, interactions_df)
        
        # Perform graph analysis
        graph_analysis = self.graph_analyzer.analyze_post_patterns(post_id, interactions_df)
        
        # Evaluate all signals
        signals = self._evaluate_signals(behavioral_features, graph_analysis)
        abnormal_signals = [s for s in signals if s['is_abnormal']]
        abnormal_count = len(abnormal_signals)
        
        # Calculate confidence score
        confidence = calculate_confidence_score(abnormal_count)
        
        # Get human-readable descriptions
        triggered = []
        detailed_signals = {}
        for signal in signals:
            detailed_signals[signal['name']] = signal['value']
            if signal['is_abnormal']:
                desc = self.signal_descriptions.get(signal['name'], signal['name'])
                triggered.append(desc)
        
        # Base result
        result = {
            'post_id': post_id,
            'total_interactions': len(interactions_df),
            'unique_users': interactions_df['user_id'].nunique(),
            'abnormal_signal_count': abnormal_count,
            'confidence': confidence,
            'label': format_instagram_ui_label(confidence),
            'tap_detail': get_instagram_tap_detail(confidence),
            'triggered_signals': triggered,
            'detailed_signals': detailed_signals
        }
        
        # Add Gemini insights if requested and available
        if use_gemini and self.gemini.is_available:
            result['gemini_insights'] = self.gemini.generate_post_insights(result)
            result['moderation_note'] = self.gemini.generate_moderation_note(result)
        
        return result
    
    def analyze_multiple_posts(self, df: pd.DataFrame, use_gemini: bool = True) -> List[Dict[str, Any]]:
        """
        Analyze multiple posts and optionally compare them with Gemini.
        
        Args:
            df: DataFrame with multiple posts
            use_gemini: Whether to use Gemini for comparison
            
        Returns:
            List of analysis results with optional comparison
        """
        results = []
        
        # Analyze each post
        for post_id in df['post_id'].unique():
            post_df = df[df['post_id'] == post_id]
            result = self.analyze_post(post_id, post_df, use_gemini=False)  # Don't use Gemini per-post yet
            results.append(result)
        
        # Add Gemini comparison if requested
        if use_gemini and self.gemini.is_available and len(results) > 1:
            comparison = self.gemini.compare_posts(results)
            for result in results:
                result['comparison_insights'] = comparison
        
        return results
    
    def _insufficient_data_response(self, post_id: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Return response for insufficient data."""
        return {
            'post_id': post_id,
            'total_interactions': len(df),
            'unique_users': df['user_id'].nunique() if len(df) > 0 else 0,
            'abnormal_signal_count': 0,
            'confidence': 0,
            'label': '',
            'tap_detail': '',
            'triggered_signals': [],
            'message': 'Insufficient data (need at least 3 interactions)'
        }
    
    def _evaluate_signals(self, behavioral_features: Dict, graph_analysis: Dict) -> List[Dict]:
        """Evaluate all 6 behavioral signals against thresholds."""
        signals = []
        
        # Signal 1: Spread Speed
        if 'spread_speed' in behavioral_features:
            signals.append({
                'name': 'spread_speed',
                'value': behavioral_features['spread_speed'].get('value', 999),
                'threshold': self.thresholds.SPREAD_SPEED_THRESHOLD_SECONDS,
                'is_abnormal': behavioral_features['spread_speed'].get('is_abnormal', False)
            })
        
        # Signal 2: Early Burst
        if 'early_burst' in behavioral_features:
            signals.append({
                'name': 'early_burst',
                'value': behavioral_features['early_burst'].get('value', 0),
                'threshold': self.thresholds.EARLY_BURST_THRESHOLD_PERCENT,
                'is_abnormal': behavioral_features['early_burst'].get('is_abnormal', False)
            })
        
        # Signal 3: Synchronization
        if 'synchronization' in behavioral_features:
            signals.append({
                'name': 'synchronization',
                'value': behavioral_features['synchronization'].get('value', 0),
                'threshold': self.thresholds.SYNC_THRESHOLD_PERCENT,
                'is_abnormal': behavioral_features['synchronization'].get('is_abnormal', False)
            })
        
        # Signal 4: User Diversity
        if 'user_diversity' in behavioral_features:
            signals.append({
                'name': 'user_diversity',
                'value': behavioral_features['user_diversity'].get('value', 1),
                'threshold': self.thresholds.USER_DIVERSITY_THRESHOLD,
                'is_abnormal': behavioral_features['user_diversity'].get('is_abnormal', False)
            })
        
        # Signal 5: Behavioral Entropy
        if 'behavioral_entropy' in behavioral_features:
            signals.append({
                'name': 'behavioral_entropy',
                'value': behavioral_features['behavioral_entropy'].get('value', 10),
                'threshold': self.thresholds.ENTROPY_THRESHOLD,
                'is_abnormal': behavioral_features['behavioral_entropy'].get('is_abnormal', False)
            })
        
        # Signal 6: Graph Clustering
        if 'graph_metrics' in graph_analysis:
            signals.append({
                'name': 'graph_clustering',
                'value': graph_analysis['graph_metrics'].get('value', 0),
                'threshold': self.thresholds.GRAPH_CLUSTERING_THRESHOLD,
                'is_abnormal': graph_analysis['graph_metrics'].get('is_abnormal', False)
            })
        
        return signals
    
    def get_confidence_only(self, post_id: str, interactions_df: pd.DataFrame) -> int:
        """Quick method - just return confidence score."""
        result = self.analyze_post(post_id, interactions_df, use_gemini=False)
        return result['confidence']
    
    def get_label_only(self, post_id: str, interactions_df: pd.DataFrame) -> str:
        """Quick method - just return UI label."""
        result = self.analyze_post(post_id, interactions_df, use_gemini=False)
        return result['label']