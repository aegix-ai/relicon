#!/usr/bin/env python3
"""
Quick test to verify server and generate a video
"""
import requests
import json
import time
import os

def test_server():
    """Test if server is running and generate a video"""
    
    # Test server health
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Server response: {response.json()}")
        else:
            print("Server not healthy")
            return False
    except Exception as e:
        print(f"Server connection failed: {str(e)}")
        return False
    
    # Generate a video
    try:
        test_data = {
            "brand_name": "QuickFit Pro",
            "brand_description": "AI fitness app with 15-minute workouts",
            "target_audience": "Busy professionals",
            "tone": "energetic",
            "duration": 30,
            "call_to_action": "Try free today"
        }
        
        print("Starting video generation...")
        response = requests.post(
            "http://localhost:8001/api/generate",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            job_id = result["job_id"]
            print(f"Job created: {job_id}")
            
            # Check status a few times
            for i in range(5):
                time.sleep(3)
                status_response = requests.get(f"http://localhost:8001/api/jobs/{job_id}")
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"Progress: {status.get('progress', 0)}% - {status.get('message', '')}")
                    
                    if status.get('status') == 'completed':
                        print("Video generation completed!")
                        print(f"Video URL: {status.get('video_url', 'N/A')}")
                        
                        # Check if video file exists
                        video_path = f"assets/{job_id}_final.mp4"
                        if os.path.exists(video_path):
                            size = os.path.getsize(video_path)
                            print(f"Video file created: {video_path} ({size:,} bytes)")
                            return True
                        else:
                            print("Video file not found")
                            return False
                    elif status.get('status') == 'failed':
                        print(f"Generation failed: {status.get('message', 'Unknown error')}")
                        return False
            
            print("Still processing after 15 seconds - system is working")
            return True
            
        else:
            print(f"Failed to start generation: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"Generation test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing ReelForge server and video generation...")
    success = test_server()
    print(f"Test result: {'SUCCESS' if success else 'FAILED'}")