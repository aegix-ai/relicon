#!/usr/bin/env python3
"""
Demo test for ReelForge AI Video Generation
"""
import requests
import json
import time
import sys

def test_video_generation():
    """Test the complete AI video generation pipeline"""
    
    # Test data for a dynamic short-form ad
    test_request = {
        "brand_name": "FlowFit",
        "brand_description": "Revolutionary fitness app that adapts to your lifestyle with AI-powered personalized workouts that take just 15 minutes a day",
        "target_audience": "Busy professionals aged 25-40",
        "tone": "energetic", 
        "duration": 30,
        "call_to_action": "Download free today"
    }
    
    print("🎬 Testing ReelForge AI Video Generation")
    print(f"📋 Brand: {test_request['brand_name']}")
    print(f"🎯 Target: {test_request['target_audience']}")
    print(f"🎵 Tone: {test_request['tone']}")
    print()
    
    try:
        # Start video generation
        print("🚀 Starting video generation...")
        response = requests.post(
            "http://localhost:8001/api/generate",
            json=test_request,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to start generation: {response.status_code}")
            print(response.text)
            return False
        
        result = response.json()
        job_id = result["job_id"]
        print(f"✅ Job created: {job_id}")
        print()
        
        # Poll for status
        print("⏳ Monitoring progress...")
        max_attempts = 30  # 5 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            status_response = requests.get(f"http://localhost:8001/api/jobs/{job_id}")
            
            if status_response.status_code == 200:
                status = status_response.json()
                progress = status.get("progress", 0)
                message = status.get("message", "Processing...")
                
                print(f"📊 Progress: {progress}% - {message}")
                
                if status.get("status") == "completed":
                    print("\n🎉 Video generation completed!")
                    
                    # Display results
                    metadata = status.get("metadata", {})
                    concept = status.get("concept", {})
                    script = status.get("script", {})
                    audio = status.get("audio", {})
                    
                    print("\n📝 Generated Content:")
                    print(f"💡 Concept: {concept.get('concept', 'N/A')}")
                    print(f"🎣 Hook: {concept.get('hook', 'N/A')}")
                    print(f"🎨 Visual Style: {concept.get('visual_style', 'N/A')}")
                    print(f"📜 Script Segments: {metadata.get('script_segments', 0)}")
                    print(f"🎙️  Audio Files: {metadata.get('audio_files', 0)}")
                    print(f"🎵 Voice Tone: {metadata.get('voice_tone', 'N/A')}")
                    
                    if script.get("segments"):
                        print("\n📋 Script Preview:")
                        for i, segment in enumerate(script["segments"][:2]):  # Show first 2 segments
                            print(f"  Segment {i+1}: \"{segment.get('voiceover', '')[:80]}...\"")
                    
                    return True
                    
                elif status.get("status") == "failed":
                    print(f"\n❌ Generation failed: {status.get('error', 'Unknown error')}")
                    return False
                    
            time.sleep(2)
            attempt += 1
        
        print("\n⏰ Timeout waiting for completion")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running on port 8001?")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_server_health():
    """Test if the server is running"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Server healthy: {health.get('status')}")
            print(f"🔑 OpenAI configured: {health.get('openai_configured')}")
            return True
        else:
            print(f"❌ Server unhealthy: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server not responding. Please start with: python run_server.py")
        return False

if __name__ == "__main__":
    print("🧪 ReelForge Demo Test\n")
    
    # Test server health first
    if not test_server_health():
        print("\n🚨 Please start the server first:")
        print("   python run_server.py")
        sys.exit(1)
    
    print()
    
    # Run the video generation test
    success = test_video_generation()
    
    if success:
        print("\n🎊 Demo completed successfully!")
        print("💫 ReelForge is creating dynamic short-form ads with AI!")
    else:
        print("\n⚠️  Demo encountered issues. Check the server logs.")
    
    print()