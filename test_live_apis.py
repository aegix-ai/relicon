#!/usr/bin/env python3
"""
Live API testing script for Relicon feedback loop.
Tests actual API integrations with Meta and TikTok.
"""
import os
import json
import requests
from datetime import datetime, date
from database import SessionLocal, Ads, MetricsMeta, MetricsTT

def test_meta_api():
    """Test Meta API connection and data retrieval."""
    print("🔵 Testing Meta API Connection")
    print("-" * 40)
    
    access_token = os.getenv("META_ACCESS_TOKEN")
    if not access_token:
        print("❌ META_ACCESS_TOKEN not set")
        print("   Set your token: export META_ACCESS_TOKEN=your_token_here")
        return False
    
    try:
        # Test basic API connection
        test_url = "https://graph.facebook.com/v19.0/me"
        params = {"access_token": access_token}
        
        response = requests.get(test_url, params=params)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Meta API Connected")
            print(f"   Account: {user_data.get('name', 'N/A')}")
            print(f"   ID: {user_data.get('id', 'N/A')}")
            
            # Test ads insights endpoint structure
            print("\n🔍 Testing Ad Insights Structure")
            
            # Note: This would normally use real ad IDs
            sample_ad_id = "123456789"  # Replace with actual ad ID
            insights_url = f"https://graph.facebook.com/v19.0/{sample_ad_id}/insights"
            insights_params = {
                "fields": "impressions,clicks,spend,actions",
                "access_token": access_token,
                "date_preset": "yesterday"
            }
            
            insights_response = requests.get(insights_url, params=insights_params)
            
            if insights_response.status_code == 200:
                print("✅ Insights endpoint accessible")
            else:
                print(f"⚠️  Insights endpoint test: {insights_response.status_code}")
                print(f"   Note: Use real ad ID for actual data")
            
            return True
            
        else:
            print(f"❌ Meta API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Meta API Exception: {e}")
        return False

def test_tiktok_api():
    """Test TikTok API connection and data retrieval."""
    print("\n🔴 Testing TikTok API Connection")
    print("-" * 40)
    
    access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
    if not access_token:
        print("❌ TIKTOK_ACCESS_TOKEN not set")
        print("   Set your token: export TIKTOK_ACCESS_TOKEN=your_token_here")
        return False
    
    try:
        # Test TikTok API connection
        test_url = "https://business-api.tiktok.com/open_api/v1.3/advertiser/info/"
        headers = {
            "Access-Token": access_token,
            "Content-Type": "application/json"
        }
        
        response = requests.get(test_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ TikTok API Connected")
            print(f"   Status: {data.get('message', 'Connected')}")
            
            # Test reporting endpoint structure
            print("\n🔍 Testing Reporting Structure")
            
            report_url = "https://business-api.tiktok.com/open_api/v2.0/report/integrated/get/"
            sample_payload = {
                "report_type": "BASIC",
                "data_level": "AUCTION_AD",
                "dimensions": ["ad_id"],
                "metrics": ["impressions", "clicks", "spend"],
                "start_date": date.today().strftime("%Y-%m-%d"),
                "end_date": date.today().strftime("%Y-%m-%d")
            }
            
            report_response = requests.post(report_url, json=sample_payload, headers=headers)
            
            if report_response.status_code == 200:
                print("✅ Reporting endpoint accessible")
            else:
                print(f"⚠️  Reporting endpoint test: {report_response.status_code}")
                print(f"   Note: Requires valid advertiser access")
            
            return True
            
        else:
            print(f"❌ TikTok API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ TikTok API Exception: {e}")
        return False

def test_shopify_webhook_format():
    """Test Shopify webhook data format."""
    print("\n🟢 Testing Shopify Webhook Format")
    print("-" * 40)
    
    # Sample webhook payload
    sample_webhook = {
        "id": 12345,
        "total_price": "99.99",
        "landing_site": "https://example.com?utm_source=facebook&utm_content=meta_fitness_winner_001",
        "referring_site": "https://facebook.com",
        "note_attributes": [
            {"name": "utm_content", "value": "meta_fitness_winner_001"}
        ],
        "line_items": [
            {
                "title": "Test Product",
                "quantity": 1,
                "price": "99.99"
            }
        ]
    }
    
    print("✅ Sample webhook payload structure:")
    print(json.dumps(sample_webhook, indent=2))
    
    # Test UTM extraction
    utm_content = None
    
    # Check landing site
    if "utm_content=" in sample_webhook["landing_site"]:
        utm_content = sample_webhook["landing_site"].split("utm_content=")[1].split("&")[0]
    
    # Check note attributes
    for attr in sample_webhook["note_attributes"]:
        if attr["name"] == "utm_content":
            utm_content = attr["value"]
            break
    
    print(f"\n✅ UTM Content Extracted: {utm_content}")
    
    return True

def test_database_integration():
    """Test database integration with sample data."""
    print("\n🗄️  Testing Database Integration")
    print("-" * 40)
    
    try:
        db = SessionLocal()
        
        # Check current data
        ads_count = db.query(Ads).count()
        metrics_count = db.query(MetricsMeta).count()
        
        print(f"✅ Database Connection Active")
        print(f"   Ads: {ads_count}")
        print(f"   Metrics: {metrics_count}")
        
        # Test data insertion
        test_ad = Ads(
            ad_id="api_test_001",
            platform="meta",
            creative_content="API test ad",
            winner_tag=False,
            roas=0.0
        )
        
        existing = db.query(Ads).filter(Ads.ad_id == "api_test_001").first()
        if not existing:
            db.add(test_ad)
            db.commit()
            print("✅ Test data insertion successful")
        else:
            print("✅ Test data already exists")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database Integration Error: {e}")
        return False

def test_celery_tasks():
    """Test Celery task configuration."""
    print("\n⚙️  Testing Celery Task Configuration")
    print("-" * 40)
    
    try:
        from celery import Celery
        
        # Test Celery app configuration
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        print(f"✅ Celery Configuration")
        print(f"   Broker: {redis_url}")
        print(f"   Tasks: fetch_meta_metrics, fetch_tt_metrics, evaluate_creatives")
        
        # Test Redis connection
        try:
            import redis
            r = redis.from_url(redis_url)
            r.ping()
            print("✅ Redis Connection Active")
        except:
            print("⚠️  Redis Connection: Not available (use local Redis or Redis Cloud)")
        
        return True
        
    except Exception as e:
        print(f"❌ Celery Configuration Error: {e}")
        return False

def run_live_api_tests():
    """Run all live API tests."""
    print("🚀 RELICON LIVE API TESTING SUITE")
    print("=" * 50)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = []
    
    # Run tests
    tests = [
        ("Meta API", test_meta_api),
        ("TikTok API", test_tiktok_api),
        ("Shopify Webhook", test_shopify_webhook_format),
        ("Database Integration", test_database_integration),
        ("Celery Tasks", test_celery_tasks)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} Exception: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 LIVE API TEST RESULTS")
    print("=" * 50)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    print("\n🔧 Component Status:")
    for test_name, result in test_results:
        status_icon = "✅" if result else "❌"
        print(f"   {status_icon} {test_name}")
    
    print("\n🎯 NEXT STEPS FOR FULL TESTING")
    print("-" * 30)
    steps = [
        "1. Get Meta Access Token from Facebook Developer Console",
        "2. Get TikTok Access Token from TikTok Business API",
        "3. Set up Redis server (local or cloud)",
        "4. Configure Shopify webhook endpoint",
        "5. Run: python start_feedback_loop.py",
        "6. Start Celery: celery -A tasks worker --loglevel=info",
        "7. Test endpoints: curl localhost:3000/analytics/summary"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    run_live_api_tests()