"""
Supabase utility functions for handling metadata storage.
"""
import os
from typing import Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseClient:
    def __init__(self):
        """Initialize Supabase client with credentials from environment variables."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment")
        self.client: Client = create_client(url, key)

    def insert_metadata(self, table: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a record into specified Supabase table.
        
        Args:
            table (str): Name of the table
            record (dict): Record to insert
            
        Returns:
            dict: Response from Supabase
        """
        try:
            response = self.client.table(table).insert(record).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            raise Exception(f"Error inserting into Supabase: {str(e)}")

    def batch_insert_metadata(self, table: str, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Insert multiple records into specified Supabase table.
        
        Args:
            table (str): Name of the table
            records (list): List of records to insert
            
        Returns:
            list: List of inserted records
        """
        try:
            response = self.client.table(table).insert(records).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Error batch inserting into Supabase: {str(e)}")

# Create a singleton instance
supabase_client = SupabaseClient()
