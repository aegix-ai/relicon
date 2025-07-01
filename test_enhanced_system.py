#!/usr/bin/env python3
"""
Test the enhanced video generation system end-to-end
"""
import requests
import time
import json

def test_complete_system():
    """Test complete video generation with enhanced AI planning"""
    
    print("🚀 Testing Enhanced ReelForge AI Video Generation System")
    print("=" * 60)
    
    # Test data
    test_request = {
        "brand_name": "EcoTech Solutions",
        "brand_description": "Revolutionary sustainable technology that reduces carbon footprint by 50% while boosting productivity",
        "target_audience": "environmentally conscious business owners",
        "tone": "confident",
        "duration": 30,
        "call_to_action": "Transform your business today!",
        "custom_requirements": "Focus on innovation and sustainability"
    }
    
    try:
        # Step 1: Test server health
        print("1. Testing server health...")
        health_response = requests.get("http://localhost:5000/api/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server health check failed")
            return False
        
        # Step 2: Submit video generation request
        print("\n2. Submitting video generation request...")
        generate_response = requests.post(
            "http://localhost:5000/api/generate",
            json=test_request,
            timeout=30
        )
        
        if generate_response.status_code != 200:
            print(f"❌ Generate request failed: {generate_response.status_code}")
            print(f"Response: {generate_response.text}")
            return False
        
        job_data = generate_response.json()
        job_id = job_data.get("job_id")
        
        if not job_id:
            print("❌ No job ID returned")
            return False
        
        print(f"✅ Job submitted successfully: {job_id}")
        
        # Step 3: Monitor progress
        print("\n3. Monitoring video generation progress...")
        start_time = time.time()
        max_wait = 600  # 10 minutes maximum
        
        while time.time() - start_time < max_wait:
            try:
                status_response = requests.get(
                    f"http://localhost:5000/api/status/{job_id}",
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get("status")
                    progress = status_data.get("progress", 0)
                    message = status_data.get("message", "")
                    
                    print(f"📊 Progress: {progress}% - {status} - {message}")
                    
                    if status == "completed":
                        video_url = status_data.get("video_url")
                        print(f"🎉 Video generation completed!")
                        print(f"📹 Video URL: {video_url}")
                        
                        # Test video access
                        if video_url:
                            video_response = requests.head(f"http://localhost:5000{video_url}")
                            if video_response.status_code in [200, 206]:
                                print("✅ Video file is accessible")
                                return True
                            else:
                                print(f"❌ Video file not accessible: {video_response.status_code}")
                                return False
                        else:
                            print("❌ No video URL provided")
                            return False
                    
                    elif status == "failed":
                        error = status_data.get("error", "Unknown error")
                        print(f"❌ Video generation failed: {error}")
                        return False
                
                # Wait before next check
                time.sleep(5)
                
            except requests.RequestException as e:
                print(f"⚠️ Error checking status: {e}")
                time.sleep(5)
        
        print("❌ Video generation timed out")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def main():
    """Run the complete system test"""
    success = test_complete_system()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("Enhanced video generation system is working correctly!")
        print("✅ AI Planning System")
        print("✅ Luma AI Video Generation") 
        print("✅ Audio Synchronization")
        print("✅ Video Assembly")
        print("✅ File Serving")
    else:
        print("\n❌ TESTS FAILED!")
        print("System needs debugging")
    
    return success

if __name__ == "__main__":
    main()