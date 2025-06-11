"""
S3 utility functions for handling data storage in AWS S3.
"""
import boto3
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class S3Client:
    def __init__(self):
        """Initialize S3 client with credentials from environment variables."""
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
        )

    def upload_to_s3(self, filepath: str, bucket: str, key: str) -> None:
        """
        Upload a file to S3 bucket.
        
        Args:
            filepath (str): Local path to the file
            bucket (str): S3 bucket name
            key (str): S3 object key (path in bucket)
        """
        try:
            self.s3.upload_file(filepath, bucket, key)
        except Exception as e:
            raise Exception(f"Error uploading to S3: {str(e)}")

    def download_from_s3(self, bucket: str, key: str, local_path: str) -> None:
        """
        Download a file from S3 bucket.
        
        Args:
            bucket (str): S3 bucket name
            key (str): S3 object key (path in bucket)
            local_path (str): Local path to save the file
        """
        try:
            self.s3.download_file(bucket, key, local_path)
        except Exception as e:
            raise Exception(f"Error downloading from S3: {str(e)}")

# Create a singleton instance
s3_client = S3Client()
