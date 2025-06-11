"""
Storage utility for handling both local and S3 storage options.
"""
import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
from datetime import datetime

from .s3 import s3_client

class StorageManager:
    def __init__(self):
        """Initialize storage manager with configuration from s3_config.yaml."""
        self.config = self._load_config()
        self.storage_mode = self.config.get('storage_mode', 'local')
        
        # Create local directories if needed
        if self.storage_mode == 'local':
            base_path = self.config['local']['base_path']
            for path in self.config['local']['paths'].values():
                full_path = os.path.join(base_path, path)
                os.makedirs(full_path, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """Load storage configuration from yaml file."""
        config_path = Path(__file__).parent.parent.parent / 'storage' / 's3_config.yaml'
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def get_storage_path(self, data_type: str) -> str:
        """
        Get the appropriate storage path based on data type and storage mode.
        
        Args:
            data_type (str): Type of data (e.g., 'token_unlocks', 'social_sentiment')
            
        Returns:
            str: Storage path
        """
        if self.storage_mode == 'local':
            base = self.config['local']['base_path']
            path = self.config['local']['paths'][data_type]
            return os.path.join(base, path)
        else:
            return self.config['s3']['paths'][data_type]

    def save_dataframe(self, df: pd.DataFrame, data_type: str, filename: str) -> str:
        """
        Save DataFrame to the configured storage location.
        
        Args:
            df (pd.DataFrame): DataFrame to save
            data_type (str): Type of data (e.g., 'token_unlocks', 'social_sentiment')
            filename (str): Name of the file
            
        Returns:
            str: Path or S3 key where the file was saved
        """
        storage_path = self.get_storage_path(data_type)
        
        if self.storage_mode == 'local':
            # Save locally
            full_path = os.path.join(storage_path, filename)
            df.to_parquet(
                full_path,
                compression=self.config['parquet']['compression'],
                row_group_size=self.config['parquet']['row_group_size'],
                index=False
            )
            return full_path
        else:
            # Save to S3
            temp_path = os.path.join('storage/temp', filename)
            os.makedirs('storage/temp', exist_ok=True)
            
            # Save temporarily
            df.to_parquet(
                temp_path,
                compression=self.config['parquet']['compression'],
                row_group_size=self.config['parquet']['row_group_size'],
                index=False
            )
            
            # Upload to S3
            s3_key = f"{storage_path}{filename}"
            s3_client.upload_to_s3(
                temp_path,
                self.config['s3']['default_bucket'],
                s3_key
            )
            
            # Clean up temp file
            os.remove(temp_path)
            return s3_key

    def read_dataframe(self, data_type: str, filename: str) -> Optional[pd.DataFrame]:
        """
        Read DataFrame from the configured storage location.
        
        Args:
            data_type (str): Type of data (e.g., 'token_unlocks', 'social_sentiment')
            filename (str): Name of the file
            
        Returns:
            Optional[pd.DataFrame]: DataFrame if file exists, None otherwise
        """
        storage_path = self.get_storage_path(data_type)
        
        if self.storage_mode == 'local':
            full_path = os.path.join(storage_path, filename)
            if os.path.exists(full_path):
                return pd.read_parquet(full_path)
        else:
            # For S3, download to temp and read
            s3_key = f"{storage_path}{filename}"
            temp_path = os.path.join('storage/temp', filename)
            os.makedirs('storage/temp', exist_ok=True)
            
            try:
                s3_client.download_from_s3(
                    self.config['s3']['default_bucket'],
                    s3_key,
                    temp_path
                )
                df = pd.read_parquet(temp_path)
                os.remove(temp_path)
                return df
            except Exception:
                return None
        
        return None

# Create a singleton instance
storage_manager = StorageManager()
