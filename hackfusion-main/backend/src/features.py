"""
Feature extraction with proper timestamp handling.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime
from .utils import DetectionThresholds
from .entropy import BehavioralEntropyAnalyzer

class BehavioralFeatureExtractor:
    def __init__(self):
        self.thresholds = DetectionThresholds()
        self.entropy = BehavioralEntropyAnalyzer()
    
    def _convert_to_datetime(self, timestamps: List) -> List[datetime]:
        """Convert string timestamps to datetime objects."""
        converted = []
        for ts in timestamps:
            if isinstance(ts, str):
                converted.append(pd.to_datetime(ts))
            else:
                converted.append(ts)
        return converted
    
    def extract_spread_speed(self, timestamps: List) -> Dict:
        """Detect abnormally fast spread speeds."""
        timestamps = self._convert_to_datetime(timestamps)
        
        if len(timestamps) < 2:
            return {'value': 999, 'is_abnormal': False}
        
        gaps = []
        for i in range(1, len(timestamps)):
            gap = (timestamps[i] - timestamps[i-1]).total_seconds()
            gaps.append(gap)
        
        avg_gap = np.mean(gaps) if gaps else 999
        return {'value': avg_gap, 'is_abnormal': avg_gap < self.thresholds.SPREAD_SPEED_THRESHOLD_SECONDS}
    
    def extract_early_burst(self, timestamps: List) -> Dict:
        """Detect if interactions happen immediately after posting."""
        timestamps = self._convert_to_datetime(timestamps)
        
        if len(timestamps) < 2:
            return {'value': 0, 'is_abnormal': False}
        
        first, last = timestamps[0], timestamps[-1]
        lifetime = (last - first).total_seconds()
        
        if lifetime == 0:
            return {'value': 1.0, 'is_abnormal': True}
        
        early = sum(1 for t in timestamps if (t - first).total_seconds() <= lifetime * 0.1)
        ratio = early / len(timestamps)
        return {'value': ratio, 'is_abnormal': ratio > self.thresholds.EARLY_BURST_THRESHOLD_PERCENT}
    
    def extract_synchronization(self, df: pd.DataFrame) -> Dict:
        """Detect users acting within 2-second windows."""
        if len(df) < 2:
            return {'value': 0, 'is_abnormal': False}
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df_sorted = df.sort_values('timestamp')
        
        times = df_sorted['timestamp'].tolist()
        users = df_sorted['user_id'].tolist()
        
        sync_users = set()
        for i in range(len(times)):
            for j in range(i+1, len(times)):
                if (times[j] - times[i]).total_seconds() <= 2:
                    sync_users.add(users[i])
                    sync_users.add(users[j])
        
        ratio = len(sync_users) / df['user_id'].nunique() if df['user_id'].nunique() > 0 else 0
        return {'value': ratio, 'is_abnormal': ratio > self.thresholds.SYNC_THRESHOLD_PERCENT}
    
    def extract_user_diversity(self, df: pd.DataFrame) -> Dict:
        """Detect low user diversity."""
        ratio = df['user_id'].nunique() / len(df) if len(df) > 0 else 1
        return {'value': ratio, 'is_abnormal': ratio < self.thresholds.USER_DIVERSITY_THRESHOLD}
    
    def extract_behavioral_entropy(self, timestamps: List, actions: List) -> Dict:
        """Detect low randomness in behavior."""
        timestamps = self._convert_to_datetime(timestamps)
        
        timing, action, _ = self.entropy.analyze_post_behavior(timestamps, actions)
        combined = (timing * 0.6 + action * 0.4) if (timing > 0 or action > 0) else 0
        return {'value': combined, 'is_abnormal': combined < self.thresholds.ENTROPY_THRESHOLD}
    
    def extract_all_features(self, post_id: str, df: pd.DataFrame) -> Dict:
        """Extract all behavioral features for a post."""
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        timestamps = df['timestamp'].tolist()
        actions = df['action_type'].tolist()
        
        return {
            'spread_speed': self.extract_spread_speed(timestamps),
            'early_burst': self.extract_early_burst(timestamps),
            'synchronization': self.extract_synchronization(df),
            'user_diversity': self.extract_user_diversity(df),
            'behavioral_entropy': self.extract_behavioral_entropy(timestamps, actions)
        }
