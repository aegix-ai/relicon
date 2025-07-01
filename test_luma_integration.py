#!/usr/bin/env python3
"""
Test Luma AI integration to verify it actually works and consumes usage
"""
import requests
import time
import json

def test_luma_generation():
    """Test a simple video generation request"""
    
    print("🧪 Testing Luma AI Integration")
    print("=" * 40)
    
    # Test simple brand
    test_request = {
        "brand_name": "TechFlow",
        "brand_description": "Innovative productivity app for modern teams",
        "target_audience": "business professionals",
        "tone": "professional",
        "duration": 15,  # Shorter duration for faster testing
        "call_to_action": "Download now!"
    }
    
    try:
        print("1. Testing server health...")
        health = requests.get("http://localhost:5000/api/health", timeout=5)
        if health.status_code == 200:
            print("✅ Server running")
        else:
            print("❌ Server not healthy")
            return
        
        print("\n2. Submitting generation request...")
        response = requests.post(
            "http://localhost:5000/api/generate",
            json=test_request,
            timeout=30
        )
        
        if response.status_code == 200:
            job_data = response.json()
            job_id = job_data["job_id"]
            print(f"✅ Job created: {job_id}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            return
        
        print("\n3. Monitoring generation progress...")
        start_time = time.time()
        
        while time.time() - start_time < 300:  # 5 minute timeout
            try:
                status = requests.get(f"http://localhost:5000/api/status/{job_id}")
                if status.status_code == 200:
                    data = status.json()
                    print(f"📊 {data['progress']}% - {data['status']} - {data['message']}")
                    
                    if data["status"] == "completed":
                        print("🎉 Generation completed!")
                        if "video_url" in data:
                            print(f"📹 Video URL: {data['video_url']}")
                        return True
                    elif data["status"] == "failed":
                        print(f"❌ Generation failed: {data.get('error', 'Unknown error')}")
                        return False
                
                time.sleep(3)
                
            except Exception as e:
                print(f"⚠️ Status check error: {e}")
                time.sleep(3)
        
        print("⏰ Generation timed out")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_luma_generation()