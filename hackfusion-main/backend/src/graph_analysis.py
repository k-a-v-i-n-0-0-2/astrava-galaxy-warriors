"""
Graph-based analysis with proper timestamp handling.
"""

import networkx as nx
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from collections import defaultdict

class InteractionGraphAnalyzer:
    def __init__(self):
        self.thresholds = type('Thresholds', (), {'GRAPH_CLUSTERING_THRESHOLD': 0.3})()
    
    def build_post_interaction_graph(self, df: pd.DataFrame, time_window_seconds: int = 10) -> nx.Graph:
        """Build graph where edges connect users who interact within time window."""
        G = nx.Graph()
        
        # Add all users as nodes
        users = df['user_id'].unique()
        G.add_nodes_from(users)
        
        if len(df) < 2:
            return G
        
        # Make sure timestamps are datetime
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df_sorted = df.sort_values('timestamp')
        
        timestamps = df_sorted['timestamp'].tolist()
        user_ids = df_sorted['user_id'].tolist()
        
        # Create edges between users who interact within the time window
        for i in range(len(df_sorted)):
            for j in range(i + 1, len(df_sorted)):
                time_diff = (timestamps[j] - timestamps[i]).total_seconds()
                
                if time_diff <= time_window_seconds:
                    user_i = user_ids[i]
                    user_j = user_ids[j]
                    
                    if user_i != user_j:
                        if G.has_edge(user_i, user_j):
                            G[user_i][user_j]['weight'] += 1
                        else:
                            G.add_edge(user_i, user_j, weight=1)
        
        return G
    
    def calculate_graph_metrics(self, G: nx.Graph) -> Dict[str, Any]:
        """Calculate graph metrics for coordination detection."""
        metrics = {
            'num_nodes': G.number_of_nodes(),
            'num_edges': G.number_of_edges(),
            'density': 0,
            'avg_clustering': 0,
            'connected_components': G.number_of_nodes(),
            'is_abnormal': False,
            'value': 0
        }
        
        if G.number_of_nodes() < 2:
            return metrics
        
        # Calculate graph density
        metrics['density'] = nx.density(G)
        
        # Calculate average clustering coefficient
        try:
            metrics['avg_clustering'] = nx.average_clustering(G, weight='weight')
        except:
            metrics['avg_clustering'] = 0
        
        metrics['connected_components'] = nx.number_connected_components(G)
        
        # COORDINATED: High clustering coefficient (>0.3)
        metrics['is_abnormal'] = metrics['avg_clustering'] > self.thresholds.GRAPH_CLUSTERING_THRESHOLD
        metrics['value'] = metrics['avg_clustering']
        
        return metrics
    
    def analyze_post_patterns(self, post_id: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Complete graph analysis for a post."""
        # Build graph with 10-second window
        G = self.build_post_interaction_graph(df, time_window_seconds=10)
        metrics = self.calculate_graph_metrics(G)
        
        # Find dense clusters
        coordinated_clusters = []
        if G.number_of_nodes() >= 3:
            components = list(nx.connected_components(G))
            for component in components:
                if len(component) >= 3:
                    subgraph = G.subgraph(component)
                    density = nx.density(subgraph)
                    if density > 0.3:
                        coordinated_clusters.append(list(component))
        
        return {
            'post_id': post_id,
            'graph_metrics': metrics,
            'coordinated_clusters': coordinated_clusters[:3],
            'is_abnormal': metrics['is_abnormal']
        }
