#!/usr/bin/env python3
"""
Manual Test Helper - Download Sample Floor Plan
Helps you test the floor plan analysis feature manually
"""

import requests
import os

def download_sample_floor_plan():
    """Download a sample floor plan image for testing"""
    
    # Sample floor plan URL (public domain)
    sample_urls = [
        # Simple 2BR floor plan
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Floor_plan_of_two-bedroom_apartment.svg/1200px-Floor_plan_of_two-bedroom_apartment.svg.png",
        # Another option
        "https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=800",
    ]
    
    output_file = "sample_floor_plan.png"
    
    print("🏠 Downloading sample floor plan...")
    print("=" * 60)
    
    for i, url in enumerate(sample_urls, 1):
        try:
            print(f"\nTrying source {i}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(output_file)
            print(f"✅ Downloaded: {output_file} ({file_size:,} bytes)")
            print(f"\n📁 Location: {os.path.abspath(output_file)}")
            print("\n" + "=" * 60)
            print("🎯 NEXT STEPS:")
            print("1. Open http://localhost:5173")
            print("2. Login: jane.smith@realestate.com / securepass123")
            print("3. Upload: sample_floor_plan.png")
            print("4. Check if it extracts bedrooms, bathrooms, sq ft")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            continue
    
    print("\n⚠️  Couldn't download sample. Please use your own floor plan image.")
    print("\n💡 Alternative: Use any floor plan image you have")
    return False

if __name__ == "__main__":
    download_sample_floor_plan()
