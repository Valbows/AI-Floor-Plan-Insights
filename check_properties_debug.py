#!/usr/bin/env python3
"""
Quick script to debug properties not showing up
"""

from app.utils.supabase_client import get_admin_db

def check_properties():
    """Check all properties in database"""
    try:
        db = get_admin_db()
        
        # Get ALL properties (not filtered by user)
        result = db.table('properties').select('*').order('created_at', desc=True).limit(10).execute()
        
        print(f"\n=== Last 10 Properties in Database ===")
        print(f"Total found: {len(result.data)}\n")
        
        for prop in result.data:
            print(f"ID: {prop['id']}")
            print(f"Agent ID: {prop.get('agent_id', 'NOT SET')}")
            print(f"Address: {prop.get('extracted_data', {}).get('address', 'No address')}")
            print(f"Status: {prop['status']}")
            print(f"Created: {prop['created_at']}")
            print(f"---")
        
        # Check users
        print(f"\n=== Users in Database ===")
        users = db.table('agents').select('id, email').execute()
        print(f"Total users: {len(users.data)}\n")
        for user in users.data:
            print(f"User ID: {user['id']}")
            print(f"Email: {user['email']}")
            # Count properties for this user
            prop_count = db.table('properties').select('id', count='exact').eq('agent_id', user['id']).execute()
            print(f"Properties: {len(prop_count.data)}")
            print(f"---")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_properties()


