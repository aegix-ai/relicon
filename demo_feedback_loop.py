#!/usr/bin/env python3
"""
Demo script for Relicon feedback loop system.
Shows how the complete system works end-to-end.
"""
import os
import asyncio
from datetime import datetime, date
from database import SessionLocal, init_db, MetricsMeta, MetricsTT, Sales, Ads
from agent import generate_next_gen_hooks

def demo_database_setup():
    """Demo database setup and sample data."""
    print("🎯 RELICON FEEDBACK LOOP DEMO")
    print("=" * 50)
    
    print("\n1. Database Setup")
    print("-" * 20)
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    db = SessionLocal()
    
    # Create sample ads with realistic data
    sample_ads = [
        Ads(
            ad_id="meta_fitness_001",
            platform="meta",
            creative_content="Transform your body in 30 days - Ready to discover the secret that fitness influencers don't want you to know?",
            winner_tag=True,
            roas=4.2
        ),
        Ads(
            ad_id="tiktok_business_001",
            platform="tiktok",
            creative_content="This one trick changed my business forever... Are you ready to scale?",
            winner_tag=True,
            roas=3.8
        ),
        Ads(
            ad_id="meta_tech_002",
            platform="meta",
            creative_content="Standard tech product advertisement without hooks",
            winner_tag=False,
            roas=1.1
        )
    ]
    
    for ad in sample_ads:
        existing = db.query(Ads).filter(Ads.ad_id == ad.ad_id).first()
        if not existing:
            db.add(ad)
    
    # Create sample metrics
    sample_metrics = [
        MetricsMeta(
            ad_id=101,
            date=date.today(),
            impressions=50000,
            clicks=2100,
            spend=500.0
        ),
        MetricsTT(
            ad_id="tiktok_business_001",
            date=date.today(),
            impressions=75000,
            clicks=3800,
            spend=380.0
        )
    ]
    
    for metric in sample_metrics:
        if isinstance(metric, MetricsMeta):
            existing = db.query(MetricsMeta).filter(
                MetricsMeta.ad_id == metric.ad_id,
                MetricsMeta.date == metric.date
            ).first()
        else:
            existing = db.query(MetricsTT).filter(
                MetricsTT.ad_id == metric.ad_id,
                MetricsTT.date == metric.date
            ).first()
        
        if not existing:
            db.add(metric)
    
    # Create sample sales
    sample_sales = [
        Sales(
            order_id=2001,
            ad_code="meta_fitness_001",
            revenue=2100.0
        ),
        Sales(
            order_id=2002,
            ad_code="tiktok_business_001",
            revenue=1444.0
        )
    ]
    
    for sale in sample_sales:
        existing = db.query(Sales).filter(Sales.order_id == sale.order_id).first()
        if not existing:
            db.add(sale)
    
    db.commit()
    print("✅ Sample data created")
    
    # Show summary
    ads_count = db.query(Ads).count()
    winners_count = db.query(Ads).filter(Ads.winner_tag == True).count()
    sales_count = db.query(Sales).count()
    
    print(f"📊 Database Summary:")
    print(f"   • Total ads: {ads_count}")
    print(f"   • Winner ads: {winners_count}")
    print(f"   • Sales records: {sales_count}")
    
    db.close()
    return True

async def demo_ai_agent():
    """Demo AI agent hook generation."""
    print("\n2. AI Agent Demo")
    print("-" * 20)
    
    db = SessionLocal()
    
    # Get sample data
    winner_ads = db.query(Ads).filter(Ads.winner_tag == True).all()
    current_ad = db.query(Ads).filter(Ads.winner_tag == False).first()
    
    if not winner_ads or not current_ad:
        print("⚠️  No sample data found")
        db.close()
        return False
    
    print(f"📈 Analyzing {len(winner_ads)} winning ads...")
    print(f"🎯 Generating hooks for: {current_ad.ad_id}")
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OpenAI API key not found - showing system structure")
        print("✅ AI agent system ready (API key needed for actual generation)")
        db.close()
        return True
    
    try:
        # Generate hooks
        hooks = await generate_next_gen_hooks(winner_ads, current_ad)
        
        print("✅ AI agent analysis complete")
        print(f"🎨 Generated {len(hooks.get('hooks', []))} hooks:")
        
        for i, hook in enumerate(hooks.get('hooks', [])[:3], 1):
            print(f"   {i}. \"{hook.get('hook_text', 'N/A')}\"")
            print(f"      Type: {hook.get('hook_type', 'N/A')} | Emotion: {hook.get('target_emotion', 'N/A')}")
            print(f"      Confidence: {hook.get('confidence_score', 0):.2f}")
        
        print(f"\n📊 Analysis: {hooks.get('analysis_summary', 'N/A')[:100]}...")
        
    except Exception as e:
        print(f"⚠️  AI agent error: {e}")
        print("✅ AI agent system ready (configuration needed)")
    
    db.close()
    return True

def demo_api_endpoints():
    """Demo API endpoints structure."""
    print("\n3. API Endpoints Demo")
    print("-" * 20)
    
    endpoints = [
        ("POST /webhook/shopify", "Process Shopify orders with UTM tracking"),
        ("GET /next-gen/{ad_id}", "Generate AI-powered hook suggestions"),
        ("GET /analytics/summary", "Get performance dashboard data"),
        ("GET /health", "System health check")
    ]
    
    print("🌐 Available API endpoints:")
    for endpoint, description in endpoints:
        print(f"   • {endpoint}")
        print(f"     {description}")
    
    print("\n📋 Scheduled Tasks:")
    tasks = [
        ("02:00 UTC", "fetch_meta_metrics", "Collect Meta advertising data"),
        ("02:15 UTC", "fetch_tt_metrics", "Collect TikTok advertising data"),
        ("03:00 UTC", "evaluate_creatives", "Calculate ROAS and identify winners")
    ]
    
    for time, task, description in tasks:
        print(f"   • {time} - {description}")
    
    return True

def demo_system_flow():
    """Demo complete system workflow."""
    print("\n4. System Workflow Demo")
    print("-" * 20)
    
    workflow_steps = [
        ("🌙 Nightly Collection", "APIs fetch ad performance data"),
        ("💰 Revenue Tracking", "Shopify webhooks capture conversions"),
        ("📊 Performance Analysis", "System calculates ROAS and identifies winners"),
        ("🤖 AI Analysis", "Agent analyzes winning patterns"),
        ("🎯 Hook Generation", "New hooks created for underperforming ads"),
        ("🔄 Continuous Learning", "System improves with each iteration")
    ]
    
    print("🔄 Complete workflow:")
    for step, description in workflow_steps:
        print(f"   {step}: {description}")
    
    print("\n🎯 Key Features:")
    features = [
        "✅ Automated metrics collection from Meta & TikTok",
        "✅ Real-time revenue tracking via Shopify webhooks",
        "✅ ROAS calculation and winner identification",
        "✅ AI-powered hook generation using GPT-4o",
        "✅ Production-ready API with error handling",
        "✅ Scalable task scheduling with Celery",
        "✅ Complete database schema for performance tracking"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    return True

async def main():
    """Run complete demo."""
    success = True
    
    # Run demo sections
    success &= demo_database_setup()
    success &= await demo_ai_agent()
    success &= demo_api_endpoints()
    success &= demo_system_flow()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 RELICON FEEDBACK LOOP SYSTEM READY")
        print("\n🚀 Next Steps:")
        print("   1. Set environment variables (see .env.example)")
        print("   2. Start API server: python start_feedback_loop.py")
        print("   3. Start Celery worker: celery -A tasks worker --loglevel=info")
        print("   4. Start Celery beat: celery -A tasks beat --loglevel=info")
        print("   5. Configure Shopify webhooks")
        print("   6. Monitor performance at /analytics/summary")
    else:
        print("⚠️  Demo completed with warnings")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())