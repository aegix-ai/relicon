#!/usr/bin/env python3
"""Direct video generation script for Node.js integration"""
import json
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def generate_video(brand_name, brand_description, duration, output_path):
    """Generate video directly using our video service"""
    try:
        from video.services.video_service import VideoService
        
        video_service = VideoService()
        
        brand_info = {
            'brand_name': brand_name,
            'brand_description': brand_description,
            'duration': duration,
            'platform': 'universal'
        }
        
        print(f"PROGRESS:30:Generating script for {brand_name}")
        
        result = video_service.create_simple_video(brand_info)
        
        print(f"PROGRESS:60:Creating video content...")
        
        if result.get('success') and result.get('video_path'):
            # Copy to the expected output path
            import shutil
            source_path = result['video_path']
            
            # Ensure the output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if os.path.exists(source_path):
                shutil.copy2(source_path, output_path)
                print(f"PROGRESS:100:Video generation completed!")
                print(f"SUCCESS:{output_path}")
                return True
            else:
                print(f"ERROR:Source video not found: {source_path}")
                return False
        else:
            print(f"ERROR:Video generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"ERROR:Exception during video generation: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python generate_video_direct.py <brand_name> <brand_description> <duration> <output_path>")
        sys.exit(1)
    
    brand_name = sys.argv[1]
    brand_description = sys.argv[2]
    duration = int(sys.argv[3])
    output_path = sys.argv[4]
    
    success = generate_video(brand_name, brand_description, duration, output_path)
    sys.exit(0 if success else 1)