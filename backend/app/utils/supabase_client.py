"""
Supabase Client Configuration
Manages connections to Supabase for database operations, auth, and storage
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class SupabaseClient:
    """
    Singleton Supabase client for database, authentication, and storage operations
    """
    
    _instance: Client = None
    _service_client: Client = None
    
    @classmethod
    def get_client(cls, use_service_role: bool = False) -> Client:
        """
        Get Supabase client instance (singleton pattern)
        
        Args:
            use_service_role: If True, uses service role key (bypasses RLS)
                             If False, uses anon key (respects RLS)
        
        Returns:
            Configured Supabase client instance
        """
        url = os.getenv('SUPABASE_URL')
        
        if not url:
            raise ValueError("SUPABASE_URL not found in environment variables")
        
        if use_service_role:
            if cls._service_client is None:
                key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
                if not key:
                    raise ValueError("SUPABASE_SERVICE_ROLE_KEY not found")
                cls._service_client = create_client(url, key)
            return cls._service_client
        else:
            if cls._instance is None:
                key = os.getenv('SUPABASE_ANON_KEY')
                if not key:
                    raise ValueError("SUPABASE_ANON_KEY not found")
                cls._instance = create_client(url, key)
            return cls._instance
    
    @classmethod
    def reset_clients(cls):
        """Reset client instances (useful for testing)"""
        cls._instance = None
        cls._service_client = None


# Convenience functions for quick access
def get_supabase_client(use_service_role: bool = False) -> Client:
    """
    Get Supabase client instance
    
    Args:
        use_service_role: Whether to use service role key (bypasses RLS)
    
    Returns:
        Configured Supabase client
    """
    return SupabaseClient.get_client(use_service_role)


def get_db():
    """Get database client (anon key with RLS)"""
    return get_supabase_client(use_service_role=False)


def get_admin_db():
    """Get admin database client (service role, bypasses RLS)"""
    return get_supabase_client(use_service_role=True)


def get_storage():
    """Get storage client for file uploads"""
    client = get_supabase_client(use_service_role=True)
    return client.storage


# Storage bucket name for floor plan images
FLOOR_PLAN_BUCKET = 'floor-plans'


def upload_floor_plan(file_path: str, file_data: bytes) -> dict:
    """
    Upload floor plan image to Supabase Storage
    
    Args:
        file_path: Destination path in storage bucket
        file_data: Binary file data
    
    Returns:
        dict with 'url' and 'path' keys
    
    Raises:
        Exception if upload fails
    """
    storage = get_storage()
    
    # Upload file
    result = storage.from_(FLOOR_PLAN_BUCKET).upload(
        file_path,
        file_data,
        file_options={"content-type": "image/png"}
    )
    
    # Get public URL
    public_url = storage.from_(FLOOR_PLAN_BUCKET).get_public_url(file_path)
    
    return {
        'url': public_url,
        'path': file_path
    }


def delete_floor_plan(file_path: str) -> bool:
    """
    Delete floor plan image from Supabase Storage
    
    Args:
        file_path: Path to file in storage bucket
    
    Returns:
        True if successful, False otherwise
    """
    try:
        storage = get_storage()
        storage.from_(FLOOR_PLAN_BUCKET).remove([file_path])
        return True
    except Exception as e:
        print(f"Error deleting floor plan: {e}")
        return False
