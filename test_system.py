#!/usr/bin/env python3
"""Test script for Relicon feedback loop system."""
import os
import sys
import asyncio
from datetime import datetime, date
from sqlalchemy.orm import Session

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, init_db, MetricsMeta, MetricsTT, Sales, Ads
from agent import generate_next_gen_hooks


def test_database_connection():
    """Test database connection and table creation."""
    try:
        print("Testing database connection...")
        init_db()
        print("✓ Database connection successful")
        
        # Test session
        db = SessionLocal()
        result = db.execute("SELECT 1").fetchone()
        db.close()
        print("✓ Database session working")
        
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False


def test_sample_data():
    """Create sample data for testing."""
    try:
        print("Creating sample data...")
        db = SessionLocal()
        
        # Create sample ads
        sample_ads = [
            Ads(
                ad_id="meta_001",
                platform="meta",
                creative_content="Transform your business with AI - Ready to discover the secret?",
                winner_tag=True,
                roas=4.5
            ),
            Ads(
                ad_id="tiktok_001", 
                platform="tiktok",
                creative_content="This changed everything for me... Are you ready?",
                winner_tag=True,
                roas=3.8
            ),
            Ads(
                ad_id="meta_002",
                platform="meta",
                creative_content="Standard ad copy without hooks",
                winner_tag=False,
                roas=1.2
            )
        ]
        
        for ad in sample_ads:
            existing = db.query(Ads).filter(Ads.ad_id == ad.ad_id).first()
            if not existing:
                db.add(ad)
        
        # Create sample metrics
        sample_metrics = [
            MetricsMeta(
                ad_id=1,
                date=date.today(),
                impressions=10000,
                clicks=500,
                spend=100.0
            ),
            MetricsTT(
                ad_id="tiktok_001",
                date=date.today(),
                impressions=15000,
                clicks=750,
                spend=150.0
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
                order_id=1001,
                ad_code="meta_001",
                revenue=450.0
            ),
            Sales(
                order_id=1002,
                ad_code="tiktok_001",
                revenue=380.0
            )
        ]
        
        for sale in sample_sales:
            existing = db.query(Sales).filter(Sales.order_id == sale.order_id).first()
            if not existing:
                db.add(sale)
        
        db.commit()
        db.close()
        
        print("✓ Sample data created successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error creating sample data: {e}")
        return False


async def test_ai_agent():
    """Test AI agent functionality."""
    try:
        print("Testing AI agent...")
        
        # Check if OpenAI API key is available
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠ OpenAI API key not found, skipping AI agent test")
            return True
        
        db = SessionLocal()
        
        # Get sample data
        winner_ads = db.query(Ads).filter(Ads.winner_tag == True).all()
        current_ad = db.query(Ads).filter(Ads.winner_tag == False).first()
        
        if not winner_ads or not current_ad:
            print("⚠ No sample data found for AI agent test")
            db.close()
            return True
        
        # Test AI agent
        hooks = await generate_next_gen_hooks(winner_ads, current_ad)
        
        db.close()
        
        print("✓ AI agent working")
        print(f"  Generated {len(hooks.get('hooks', []))} hooks")
        print(f"  Analysis: {hooks.get('analysis_summary', 'No summary')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ AI agent error: {e}")
        return False


def test_api_imports():
    """Test API imports and dependencies."""
    try:
        print("Testing API imports...")
        
        # Test FastAPI imports
        from fastapi import FastAPI
        from pydantic import BaseModel
        print("✓ FastAPI imports working")
        
        # Test Celery imports
        from celery import Celery
        print("✓ Celery imports working")
        
        # Test database imports
        from sqlalchemy import create_engine
        print("✓ SQLAlchemy imports working")
        
        # Test main modules
        import main
        import tasks
        import agent
        print("✓ All custom modules importing successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False


def print_system_info():
    """Print system information."""
    print("\n" + "="*50)
    print("RELICON FEEDBACK LOOP SYSTEM TEST")
    print("="*50)
    print(f"Test time: {datetime.now().isoformat()}")
    print(f"Database URL: {os.getenv('DATABASE_URL', 'Not set')}")
    print(f"OpenAI API Key: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    print(f"Redis URL: {os.getenv('REDIS_URL', 'Not set')}")
    print("-"*50)


async def main():
    """Run all tests."""
    print_system_info()
    
    tests = [
        ("API Imports", test_api_imports),
        ("Database Connection", test_database_connection),
        ("Sample Data Creation", test_sample_data),
        ("AI Agent", test_ai_agent),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[{passed + 1}/{total}] {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} failed: {e}")
    
    print(f"\n" + "="*50)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All systems operational!")
        print("\nNEXT STEPS:")
        print("1. Set environment variables in .env file")
        print("2. Start the API server: uvicorn main:app --host 0.0.0.0 --port 3000")
        print("3. Start Celery worker: celery -A tasks worker --loglevel=info")
        print("4. Start Celery beat: celery -A tasks beat --loglevel=info")
    else:
        print("⚠ Some tests failed. Check the errors above.")
    
    print("="*50)


if __name__ == "__main__":
    asyncio.run(main())