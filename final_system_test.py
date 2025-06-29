#!/usr/bin/env python3
"""
Final comprehensive test of the bulletproof system
"""

import requests
import time
import json

def test_end_to_end():
    """Test complete video generation end-to-end"""
    print("🎬 Testing bulletproof ReelForge system...")
    
    # Test data
    request_data = {
        "brand_name": "TechFlow AI",
        "brand_description": "Revolutionary AI automation platform that transforms business workflows with intelligent solutions",
        "target_audience": "Tech entrepreneurs and business owners",
        "tone": "exciting",
        "duration": 30,
        "call_to_action": "Start your free trial today"
    }
    
    try:
        # Submit generation request
        print("📤 Submitting video generation request...")
        response = requests.post('http://localhost:5000/api/generate', json=request_data, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
        result = response.json()
        job_id = result.get('job_id')
        
        if not job_id:
            print("❌ No job ID received")
            return False
            
        print(f"✅ Job created: {job_id}")
        
        # Monitor progress
        max_wait = 120  # 2 minutes max
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status_response = requests.get(f'http://localhost:5000/api/status/{job_id}', timeout=5)
            
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"📊 Status: {status.get('status')} - Progress: {status.get('progress')}% - {status.get('message', '')}")
                
                if status.get('status') == 'completed':
                    video_url = status.get('video_url')
                    if video_url:
                        print(f"✅ SUCCESS! Video completed: {video_url}")
                        return True
                    else:
                        print("❌ Completed but no video URL")
                        return False
                        
                elif status.get('status') == 'failed':
                    print(f"❌ Generation failed: {status.get('message', 'Unknown error')}")
                    return False
            
            time.sleep(2)
        
        print("❌ Test timed out")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 ReelForge Final System Test")
    print("="*50)
    
    if test_end_to_end():
        print("\n🏆 SYSTEM IS BULLETPROOF AND READY!")
        print("🚀 Professional-grade video generation working flawlessly!")
    else:
        print("\n💥 CRITICAL ISSUE - System needs immediate attention")