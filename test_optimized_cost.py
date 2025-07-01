#!/usr/bin/env python3
"""
Test the cost-optimized video generation system
"""
import requests
import time

def test_cost_optimized_generation():
    """Test with the new cost-optimized system"""
    
    print("🧪 Testing Cost-Optimized Video Generation")
    print("=" * 45)
    
    # Test with same parameters that cost $8 before
    test_request = {
        "brand_name": "EcoTech Solutions",
        "brand_description": "Sustainable technology for smart homes",
        "target_audience": "environmentally conscious homeowners",
        "tone": "friendly",
        "duration": 15,  # 15 seconds should now use only 2 segments
        "call_to_action": "Go green today!"
    }
    
    try:
        print("1. Testing server...")
        health = requests.get("http://localhost:5000/api/health", timeout=5)
        if health.status_code != 200:
            print("❌ Server not running")
            return
        print("✅ Server running")
        
        print("\n2. Submitting cost-optimized request...")
        print(f"   Duration: {test_request['duration']}s (should create 2 segments max)")
        
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
        
        print("\n3. Monitoring for cost efficiency...")
        start_time = time.time()
        segment_count = 0
        
        while time.time() - start_time < 180:  # 3 minute timeout
            try:
                status = requests.get(f"http://localhost:5000/api/status/{job_id}")
                if status.status_code == 200:
                    data = status.json()
                    message = data['message']
                    
                    # Count video segments being processed
                    if "Processing video segment" in message:
                        segment_num = int(message.split("segment ")[1])
                        segment_count = max(segment_count, segment_num)
                    
                    print(f"📊 {data['progress']}% - {data['status']} - {message}")
                    
                    if data["status"] == "completed":
                        print(f"\n🎉 Generation completed!")
                        print(f"💰 Segments created: {segment_count}")
                        estimated_cost = segment_count * 1.6
                        print(f"💰 Estimated cost: ${estimated_cost:.2f}")
                        
                        if segment_count <= 2:
                            print("✅ COST OPTIMIZATION SUCCESS!")
                            print(f"   Previous: 5 segments = $8.00")
                            print(f"   Current:  {segment_count} segments = ${estimated_cost:.2f}")
                            savings = 8.00 - estimated_cost
                            print(f"   Savings:  ${savings:.2f} ({savings/8*100:.0f}%)")
                        else:
                            print("⚠️  Still too many segments - needs further optimization")
                        
                        return True
                        
                    elif data["status"] == "failed":
                        print(f"❌ Generation failed: {data.get('error', 'Unknown error')}")
                        return False
                
                time.sleep(3)
                
            except Exception as e:
                print(f"⚠️ Status check error: {e}")
                time.sleep(3)
        
        print("⏰ Test timed out")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_cost_optimized_generation()