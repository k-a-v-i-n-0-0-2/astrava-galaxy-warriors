"""Data loading and validation module for interaction events."""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import os


class InteractionDataLoader:
    """
    Loads and validates platform interaction events.
    
    In production, this would connect to event streams or data lakes.
    For this implementation, we support CSV and in-memory data structures.
    """
    
    def __init__(self, data_source: Optional[str] = None):
        """
        Initialize the data loader.
        
        Args:
            data_source: Either a file path (str) or pandas DataFrame
        """
        self.data_source = data_source
        self.required_columns = ['post_id', 'user_id', 'timestamp', 'action_type']
        self.valid_actions = ['share', 'repost', 'like', 'comment']
    
    def load_data(self) -> pd.DataFrame:
        """
        Load interaction data from source.
        
        Returns:
            DataFrame with validated interaction events
            
        Raises:
            ValueError: If data format is invalid or missing required columns
            FileNotFoundError: If data file doesn't exist
        """
        if self.data_source is None:
            # Return empty DataFrame if no source provided
            print("Warning: No data source provided, returning empty DataFrame")
            return pd.DataFrame(columns=self.required_columns)
        
        # Load based on source type
        if isinstance(self.data_source, str):
            # Assume file path
            if not os.path.exists(self.data_source):
                raise FileNotFoundError(f"Data file not found: {self.data_source}")
            
            try:
                df = pd.read_csv(self.data_source)
                print(f"✓ Successfully loaded data from {self.data_source}")
            except Exception as e:
                raise ValueError(f"Failed to read CSV file: {e}")
                
        elif isinstance(self.data_source, pd.DataFrame):
            df = self.data_source.copy()
            print("✓ Successfully loaded data from DataFrame")
        else:
            raise ValueError(f"Unsupported data source type: {type(self.data_source)}")
        
        # Validate and clean data
        df = self._validate_data(df)
        
        return df
    
    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and clean interaction data.
        
        Args:
            df: Raw DataFrame to validate
        
        Returns:
            Cleaned and validated DataFrame
        """
        # Check for required columns
        missing_cols = set(self.required_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Make a copy to avoid modifying original
        df_clean = df.copy()
        
        # Convert timestamp to datetime
        try:
            df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'])
        except Exception as e:
            raise ValueError(f"Failed to parse timestamps: {e}")
        
        # Validate action types
        invalid_actions = ~df_clean['action_type'].isin(self.valid_actions)
        if invalid_actions.any():
            invalid_values = df_clean.loc[invalid_actions, 'action_type'].unique()
            print(f"Warning: Removing rows with invalid action types: {invalid_values}")
            df_clean = df_clean[~invalid_actions]
        
        # Remove duplicates (same user, same post, same timestamp, same action)
        df_clean = df_clean.drop_duplicates(
            subset=['post_id', 'user_id', 'timestamp', 'action_type']
        )
        
        # Sort by timestamp
        df_clean = df_clean.sort_values('timestamp')
        
        # Reset index
        df_clean = df_clean.reset_index(drop=True)
        
        return df_clean
    
    def group_by_post(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Group interaction data by post_id.
        
        Args:
            df: Interaction DataFrame
        
        Returns:
            Dictionary mapping post_id to its interaction DataFrame
        """
        if df.empty:
            return {}
        
        groups = {}
        for post_id, group in df.groupby('post_id'):
            groups[post_id] = group.sort_values('timestamp').reset_index(drop=True)
        
        return groups
