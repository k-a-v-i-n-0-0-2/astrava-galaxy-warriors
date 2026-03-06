"""Entropy and randomness calculations for behavioral analysis."""

import numpy as np
from scipy.stats import entropy
from typing import List, Tuple
from collections import Counter


class BehavioralEntropyAnalyzer:
    """
    Calculates entropy-based metrics to measure randomness in interaction patterns.
    
    Low entropy indicates scripted or automated behavior with predictable patterns.
    High entropy indicates natural human variation in timing and actions.
    """
    
    @staticmethod
    def calculate_timing_entropy(timestamps: List, bins: int = 10) -> float:
        """
        Calculate Shannon entropy of interaction timing distribution.
        
        Args:
            timestamps: List of datetime objects
            bins: Number of bins for histogram
        
        Returns:
            Entropy value in bits (higher = more random, lower = more scripted)
        """
        if len(timestamps) < 2:
            return 0.0
        
        # Convert to seconds since first interaction
        time_deltas = [(ts - timestamps[0]).total_seconds() for ts in timestamps]
        
        if len(set(time_deltas)) == 1:
            return 0.0  # All identical timestamps -> zero entropy
        
        # Create histogram of interaction times
        hist, _ = np.histogram(time_deltas, bins=bins)
        
        # Normalize to probability distribution
        prob_dist = hist / np.sum(hist)
        
        # Remove zero probabilities for entropy calculation
        prob_dist = prob_dist[prob_dist > 0]
        
        # Calculate Shannon entropy (bits)
        shannon_entropy = entropy(prob_dist, base=2)
        
        return shannon_entropy
    
    @staticmethod
    def calculate_action_entropy(action_sequence: List[str]) -> float:
        """
        Calculate entropy of action type distribution.
        
        Args:
            action_sequence: List of action types [share, repost, like, comment]
        
        Returns:
            Entropy value in bits
        """
        if not action_sequence:
            return 0.0
        
        # Count frequency of each action type
        action_counts = Counter(action_sequence)
        total_actions = len(action_sequence)
        
        # Calculate probability distribution
        prob_dist = [count / total_actions for count in action_counts.values()]
        
        # Calculate Shannon entropy
        shannon_entropy = entropy(prob_dist, base=2)
        
        return shannon_entropy
    
    @staticmethod
    def calculate_sequence_randomness(intervals: List[float]) -> float:
        """
        Calculate coefficient of variation to measure regularity of intervals.
        
        Args:
            intervals: List of time differences between consecutive interactions
        
        Returns:
            Coefficient of variation (lower = more regular/scripted)
        """
        if len(intervals) < 2:
            return 0.0
        
        intervals_array = np.array(intervals)
        
        # Handle zero standard deviation case
        if np.std(intervals_array) == 0:
            return 0.0
        
        # Coefficient of variation = std/mean
        cv = np.std(intervals_array) / np.mean(intervals_array)
        
        return cv
    
    def analyze_post_behavior(self, timestamps: List, actions: List[str]) -> Tuple[float, float, float]:
        """
        Comprehensive behavioral randomness analysis for a post.
        
        Args:
            timestamps: List of interaction timestamps
            actions: List of action types
        
        Returns:
            Tuple of (timing_entropy, action_entropy, interval_regularity)
        """
        timing_entropy = self.calculate_timing_entropy(timestamps)
        action_entropy = self.calculate_action_entropy(actions)
        
        # Calculate intervals between consecutive timestamps
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        interval_regularity = self.calculate_sequence_randomness(intervals)
        
        return timing_entropy, action_entropy, interval_regularity
