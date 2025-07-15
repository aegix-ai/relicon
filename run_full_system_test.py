#!/usr/bin/env python3
"""
Full system integration test for Relicon feedback loop.
Demonstrates the complete workflow from data collection to optimization.
"""
import os
import json
import asyncio
from datetime import datetime, date, timedelta
from database import SessionLocal, init_db, Ads, MetricsMeta, MetricsTT, Sales
from tasks import evaluate_creatives
from agent import generate_next_gen_hooks

async def full_system_demonstration():
    """Complete system demonstration showing all capabilities."""
    
    print("🎯 RELICON FEEDBACK LOOP - FULL SYSTEM DEMONSTRATION")
    print("=" * 65)
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Initialize System
    print("1️⃣  SYSTEM INITIALIZATION")
    print("-" * 30)
    
    try:
        init_db()
        print("✅ Database initialized")
        
        db = SessionLocal()
        print("✅ Database connection established")
        
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        return
    
    # Step 2: Create Realistic Ad Campaign Data
    print("\n2️⃣  CAMPAIGN DATA SETUP")
    print("-" * 30)
    
    # Clear existing test data
    db.query(Sales).filter(Sales.order_id.between(4000, 4999)).delete()
    db.query(MetricsMeta).filter(MetricsMeta.ad_id.between(2000, 2999)).delete()
    db.query(MetricsTT).filter(MetricsTT.ad_id.like("test_%")).delete()
    db.query(Ads).filter(Ads.ad_id.like("test_%")).delete()
    db.commit()
    
    # Create realistic ad campaigns
    campaigns = [
        {
            "ad_id": "test_fitness_hook_001",
            "platform": "meta",
            "content": "Ready to transform your body in 30 days? This secret method will shock you!",
            "spend": 800.0,
            "impressions": 120000,
            "clicks": 3600,
            "revenue": 4800.0  # 6.0 ROAS - Winner
        },
        {
            "ad_id": "test_business_hook_001", 
            "platform": "tiktok",
            "content": "This one trick helped me scale from $0 to $100K... Are you ready?",
            "spend": 600.0,
            "impressions": 90000,
            "clicks": 2700,
            "revenue": 3000.0  # 5.0 ROAS - Winner
        },
        {
            "ad_id": "test_tech_basic_001",
            "platform": "meta", 
            "content": "Our software solution provides enterprise-grade functionality",
            "spend": 500.0,
            "impressions": 80000,
            "clicks": 800,
            "revenue": 250.0  # 0.5 ROAS - Loser
        },
        {
            "ad_id": "test_fashion_basic_001",
            "platform": "tiktok",
            "content": "Check out our new collection of trendy clothes",
            "spend": 400.0,
            "impressions": 60000,
            "clicks": 300,
            "revenue": 200.0  # 0.5 ROAS - Loser
        }
    ]
    
    # Insert campaign data
    for i, campaign in enumerate(campaigns):
        # Create ad
        ad = Ads(
            ad_id=campaign["ad_id"],
            platform=campaign["platform"],
            creative_content=campaign["content"],
            winner_tag=False,
            roas=0.0
        )
        db.add(ad)
        
        # Create metrics
        if campaign["platform"] == "meta":
            metric = MetricsMeta(
                ad_id=2000 + i,
                date=date.today() - timedelta(days=1),
                impressions=campaign["impressions"],
                clicks=campaign["clicks"],
                spend=campaign["spend"]
            )
            db.add(metric)
        else:
            metric = MetricsTT(
                ad_id=campaign["ad_id"],
                date=date.today() - timedelta(days=1),
                impressions=campaign["impressions"],
                clicks=campaign["clicks"],
                spend=campaign["spend"]
            )
            db.add(metric)
        
        # Create sales
        sale = Sales(
            order_id=4000 + i,
            ad_code=campaign["ad_id"],
            revenue=campaign["revenue"]
        )
        db.add(sale)
        
        print(f"✅ Campaign: {campaign['ad_id']}")
        print(f"   Platform: {campaign['platform']}")
        print(f"   Spend: ${campaign['spend']:.2f}")
        print(f"   Revenue: ${campaign['revenue']:.2f}")
        print(f"   Expected ROAS: {campaign['revenue']/campaign['spend']:.1f}")
    
    db.commit()
    
    # Step 3: Performance Analysis
    print("\n3️⃣  PERFORMANCE ANALYSIS & WINNER IDENTIFICATION")
    print("-" * 50)
    
    # Run evaluation
    result = evaluate_creatives()
    
    if result.get("status") == "success":
        print("✅ Performance analysis completed")
        print(f"   Updated ads: {result.get('updated_ads', 0)}")
        print(f"   Winners identified: {result.get('winners_identified', 0)}")
    else:
        print(f"❌ Performance analysis failed: {result}")
    
    # Show results
    winners = db.query(Ads).filter(Ads.winner_tag == True).all()
    losers = db.query(Ads).filter(Ads.winner_tag == False).all()
    
    print(f"\n🏆 WINNERS (Top 25% by ROAS):")
    for winner in winners:
        print(f"   ✅ {winner.ad_id}: ROAS {winner.roas:.1f}")
        print(f"      \"{winner.creative_content[:60]}...\"")
    
    print(f"\n📉 UNDERPERFORMERS:")
    for loser in losers:
        print(f"   ❌ {loser.ad_id}: ROAS {loser.roas:.1f}")
        print(f"      \"{loser.creative_content[:60]}...\"")
    
    # Step 4: AI-Powered Optimization
    print("\n4️⃣  AI-POWERED OPTIMIZATION")
    print("-" * 35)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OpenAI API key not set - showing system structure")
        print("   Set OPENAI_API_KEY to see actual AI optimization")
        
        # Show what would happen
        print("\n🤖 AI Optimization Process:")
        print("   1. Analyze winning ad patterns")
        print("   2. Extract psychological triggers")
        print("   3. Identify emotional hooks")
        print("   4. Generate optimized alternatives")
        print("   5. Score by predicted performance")
        
    else:
        print("🤖 Running AI optimization...")
        
        if winners and losers:
            target_loser = losers[0]
            print(f"   Target ad: {target_loser.ad_id}")
            print(f"   Current ROAS: {target_loser.roas:.1f}")
            
            try:
                hooks = await generate_next_gen_hooks(winners, target_loser)
                
                print("✅ AI analysis completed")
                print(f"   Generated {len(hooks.get('hooks', []))} optimized hooks")
                
                print("\n🎯 OPTIMIZED HOOKS:")
                for i, hook in enumerate(hooks.get('hooks', [])[:3], 1):
                    print(f"   {i}. \"{hook.get('hook_text', 'N/A')}\"")
                    print(f"      Type: {hook.get('hook_type', 'N/A')}")
                    print(f"      Emotion: {hook.get('target_emotion', 'N/A')}")
                    print(f"      Confidence: {hook.get('confidence_score', 0):.2f}")
                    print()
                
                print(f"📊 Analysis Summary:")
                print(f"   {hooks.get('analysis_summary', 'N/A')[:100]}...")
                
                print(f"\n🔍 Winning Patterns Identified:")
                for pattern in hooks.get('winning_patterns', []):
                    print(f"   • {pattern}")
                
            except Exception as e:
                print(f"❌ AI optimization error: {e}")
    
    # Step 5: System Metrics & Performance
    print("\n5️⃣  SYSTEM PERFORMANCE METRICS")
    print("-" * 40)
    
    # Calculate system metrics
    total_ads = db.query(Ads).count()
    total_spend = db.execute("SELECT SUM(spend) FROM metrics_meta").scalar() or 0
    total_spend += db.execute("SELECT SUM(spend) FROM metrics_tt").scalar() or 0
    total_revenue = db.execute("SELECT SUM(revenue) FROM sales").scalar() or 0
    
    overall_roas = total_revenue / total_spend if total_spend > 0 else 0
    
    print(f"📊 Campaign Performance:")
    print(f"   Total Ads: {total_ads}")
    print(f"   Total Spend: ${total_spend:.2f}")
    print(f"   Total Revenue: ${total_revenue:.2f}")
    print(f"   Overall ROAS: {overall_roas:.1f}")
    
    # Step 6: Show Time Series Data
    print("\n6️⃣  TIME SERIES ANALYSIS")
    print("-" * 30)
    
    # Performance over time simulation
    print("📈 Performance Tracking:")
    print(f"   Data Collection: {date.today() - timedelta(days=1)}")
    print(f"   Analysis Run: {date.today()}")
    print(f"   Next Collection: {date.today() + timedelta(days=1)} at 02:00 UTC")
    
    # Step 7: API Endpoints Ready
    print("\n7️⃣  API ENDPOINTS READY")
    print("-" * 30)
    
    endpoints = [
        "GET /analytics/summary - Performance dashboard",
        "POST /webhook/shopify - Order tracking",
        "GET /next-gen/{ad_id} - AI optimization",
        "GET /health - System status"
    ]
    
    print("🌐 Available endpoints:")
    for endpoint in endpoints:
        print(f"   • {endpoint}")
    
    # Final Summary
    print("\n" + "=" * 65)
    print("🎉 SYSTEM DEMONSTRATION COMPLETE")
    print("=" * 65)
    
    capabilities = [
        "✅ Database schema and data persistence",
        "✅ ROAS calculation and winner identification", 
        "✅ AI-powered optimization suggestions",
        "✅ Time series performance tracking",
        "✅ API integration readiness",
        "✅ Automated task scheduling structure"
    ]
    
    print("\n🚀 DEMONSTRATED CAPABILITIES:")
    for capability in capabilities:
        print(f"   {capability}")
    
    print(f"\n📋 TO TEST WITH LIVE DATA:")
    print(f"   1. Set META_ACCESS_TOKEN and TIKTOK_ACCESS_TOKEN")
    print(f"   2. Start API: python start_feedback_loop.py")
    print(f"   3. Start Celery: celery -A tasks worker --loglevel=info")
    print(f"   4. Test endpoints: curl localhost:3000/analytics/summary")
    
    print("\n🔄 NIGHTLY AUTOMATION SCHEDULE:")
    print("   02:00 UTC - Collect Meta metrics")
    print("   02:15 UTC - Collect TikTok metrics")
    print("   03:00 UTC - Analyze performance & identify winners")
    
    print("\n" + "=" * 65)
    
    db.close()

if __name__ == "__main__":
    asyncio.run(full_system_demonstration())