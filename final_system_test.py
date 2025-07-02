#!/usr/bin/env python3
"""
Final comprehensive test of the optimized system
"""
import requests
import time

def test_optimized_system():
    """Test complete optimized video generation"""
    
    print("🎯 FINAL OPTIMIZED SYSTEM TEST")
    print("=" * 40)
    
    # Test with cost-optimized parameters
    test_request = {
        "brand_name": "FlowFit", 
        "brand_description": "AI-powered fitness app that creates personalized workout plans",
        "target_audience": "fitness enthusiasts aged 25-40",
        "tone": "energetic",
        "duration": 15,  # Should create exactly 2 segments with ray-1-6 model
        "call_to_action": "Start your transformation!"
    }
    
    try:
        print("1. Testing server health...")
        health = requests.get("http://localhost:5000/api/health", timeout=5)
        if health.status_code != 200:
            print("❌ Server not responding")
            return False
        print("✅ Server healthy")
        
        print("\n2. Submitting optimized generation...")
        print(f"   Brand: {test_request['brand_name']}")
        print(f"   Duration: {test_request['duration']}s")
        print(f"   Expected: 2 segments, ray-1-6 model")
        print(f"   Expected cost: ~$2.42")
        
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
            print(f"❌ Generation failed: {response.status_code}")
            return False
        
        print("\n3. Monitoring generation progress...")
        start_time = time.time()
        segment_count = 0
        last_progress = 0
        
        while time.time() - start_time < 180:  # 3 minute timeout
            try:
                status = requests.get(f"http://localhost:5000/api/status/{job_id}")
                if status.status_code == 200:
                    data = status.json()
                    
                    # Track segments for cost calculation
                    if "Processing video segment" in data['message']:
                        try:
                            segment_num = int(data['message'].split("segment ")[1])
                            segment_count = max(segment_count, segment_num)
                        except:
                            pass
                    
                    # Show progress only when it changes
                    if data['progress'] != last_progress:
                        print(f"📊 {data['progress']}% - {data['message']}")
                        last_progress = data['progress']
                    
                    if data["status"] == "completed":
                        print(f"\n🎉 GENERATION COMPLETED!")
                        
                        # Cost analysis
                        if segment_count > 0:
                            luma_cost = segment_count * 1.20  # ray-1-6 pricing
                            tts_cost = segment_count * 0.015
                            planning_cost = 0.008
                            total_cost = luma_cost + tts_cost + planning_cost
                            
                            print(f"💰 COST BREAKDOWN:")
                            print(f"   Segments created: {segment_count}")
                            print(f"   Luma (ray-1-6): ${luma_cost:.2f}")
                            print(f"   TTS: ${tts_cost:.3f}")
                            print(f"   Planning: ${planning_cost:.3f}")
                            print(f"   TOTAL: ${total_cost:.2f}")
                            
                            if segment_count <= 2 and total_cost <= 3.00:
                                print("✅ COST OPTIMIZATION SUCCESS!")
                            else:
                                print("⚠️  Cost higher than expected")
                        
                        if "video_url" in data:
                            print(f"📹 Video ready: {data['video_url']}")
                        
                        return True
                        
                    elif data["status"] == "failed":
                        print(f"❌ Generation failed: {data.get('error', 'Unknown error')}")
                        return False
                
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠️ Status check error: {e}")
                time.sleep(2)
        
        print("⏰ Test timed out")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run final system test"""
    print("REELFORGE FINAL SYSTEM VALIDATION")
    print("Testing complete pipeline with cost optimizations")
    print("-" * 50)
    
    success = test_optimized_system()
    
    if success:
        print("\n✅ SYSTEM READY FOR PRODUCTION")
        print("Cost-optimized video generation working correctly")
        print("Ready to implement autonomous learning features")
    else:
        print("\n❌ SYSTEM NEEDS ATTENTION")
        print("Fix issues before proceeding to autonomous learning")

if __name__ == "__main__":
    main()