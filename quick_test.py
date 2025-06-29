#!/usr/bin/env python3
"""
Quick test to verify server and generate a video
"""
import requests
import time
import json

def test_server():
    """Test if server is running and generate a video"""
    server_url = "http://localhost:8001"
    
    print("QUICK SERVER AND VIDEO GENERATION TEST")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing server health...")
    try:
        response = requests.get(f"{server_url}/health")
        if response.status_code == 200:
            print("✓ Server is running")
        else:
            print(f"✗ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to server: {e}")
        return False
    
    # Test 2: Generate a video
    print("2. Requesting video generation...")
    try:
        request_data = {
            "brand_name": "FlowFit",
            "brand_description": "A mobile fitness app with 15-minute workouts for busy professionals",
            "target_audience": "Working professionals aged 25-40",
            "tone": "energetic",
            "duration": 25,
            "call_to_action": "Download the app today!"
        }
        
        response = requests.post(f"{server_url}/api/generate", json=request_data)
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get("job_id")
            print(f"✓ Video generation started: {job_id}")
            
            # Test 3: Monitor progress
            print("3. Monitoring progress...")
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                
                status_response = requests.get(f"{server_url}/api/status/{job_id}")
                if status_response.status_code == 200:
                    status = status_response.json()
                    progress = status.get("progress", 0)
                    message = status.get("message", "")
                    status_value = status.get("status", "")
                    
                    print(f"   Progress: {progress}% - {message}")
                    
                    if status_value == "completed":
                        video_url = status.get("video_url")
                        print(f"✓ Video completed: {video_url}")
                        return True
                    elif status_value == "failed":
                        error = status.get("error", "Unknown error")
                        print(f"✗ Video generation failed: {error}")
                        return False
                
            print("✗ Video generation timed out")
            return False
        else:
            print(f"✗ Generation request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    if success:
        print("\n🎉 SUCCESS: ReelForge is working perfectly!")
        print("✓ Server running")
        print("✓ AI generation working") 
        print("✓ Video creation successful")
        print("✓ Complete pipeline functional")
    else:
        print("\n💥 FAILED: System needs debugging")
    
    exit(0 if success else 1)