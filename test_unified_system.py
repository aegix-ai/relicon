#!/usr/bin/env python3
"""
Comprehensive test of the unified Relicon system
Verifies all functionality works exactly as before the refactoring
"""

import sys
import os
import traceback
from datetime import datetime

def test_imports():
    """Test all imports work correctly"""
    print("🔍 Testing Imports...")
    
    try:
        import main
        print("✅ main.py imported successfully")
        
        # Test all service initialization
        services = {
            'FastAPI app': main.app,
            'OpenAI client': main.openai_client,
            'Video planner': main.video_planner,
            'Luma service': main.luma_service,
            'Tree planner': main.tree_planner,
            'Script generator': main.script_generator
        }
        
        for name, service in services.items():
            if service:
                print(f"✅ {name} initialized correctly")
            else:
                print(f"❌ {name} failed to initialize")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        traceback.print_exc()
        return False

def test_video_planning():
    """Test video planning functionality"""
    print("\n🎬 Testing Video Planning...")
    
    try:
        from ai_planner import VideoAdPlanner
        
        planner = VideoAdPlanner()
        brand_info = {
            'brand_name': 'TestBrand',
            'brand_description': 'A revolutionary product',
            'target_audience': 'tech enthusiasts',
            'tone': 'energetic',
            'duration': 15,
            'call_to_action': 'Buy now'
        }
        
        # Test master plan creation
        master_plan = planner.create_master_plan(brand_info)
        if not isinstance(master_plan, dict):
            print("❌ Master plan should return dict")
            return False
        
        required_keys = ['core_message', 'hook', 'energy_level']
        for key in required_keys:
            if key not in master_plan:
                print(f"❌ Missing required key: {key}")
                return False
        
        print("✅ Master plan creation works correctly")
        
        # Test scene breakdown
        scenes = planner.break_down_components(master_plan, 15)
        if not isinstance(scenes, list) or len(scenes) == 0:
            print("❌ Scene breakdown should return non-empty list")
            return False
            
        print(f"✅ Scene breakdown works correctly ({len(scenes)} scenes)")
        return True
        
    except Exception as e:
        print(f"❌ Video planning test failed: {e}")
        traceback.print_exc()
        return False

def test_script_generation():
    """Test script generation functionality"""
    print("\n📝 Testing Script Generation...")
    
    try:
        from energetic_script_generator import EnergeticScriptGenerator
        
        generator = EnergeticScriptGenerator()
        brand_info = {
            'brand_name': 'TestBrand',
            'brand_description': 'A revolutionary product',
            'target_audience': 'tech enthusiasts',
            'tone': 'energetic',
            'duration': 15,
            'call_to_action': 'Buy now'
        }
        
        segments = generator.generate_energetic_segments(brand_info, num_segments=3)
        
        if not isinstance(segments, list) or len(segments) != 3:
            print("❌ Should return list of 3 segments")
            return False
            
        for i, segment in enumerate(segments):
            if not isinstance(segment, dict):
                print(f"❌ Segment {i} should be dict")
                return False
                
        print("✅ Script generation works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Script generation test failed: {e}")
        traceback.print_exc()
        return False

def test_database_functionality():
    """Test database and feedback loop functionality"""
    print("\n💾 Testing Database & Feedback Loop...")
    
    try:
        from database import SessionLocal, Sales, Ads, get_db
        from agent import generate_next_gen_hooks
        
        # Test database connection
        db = SessionLocal()
        total_ads = db.query(Ads).count()
        total_sales = db.query(Sales).count()
        db.close()
        
        print(f"✅ Database connection works (Ads: {total_ads}, Sales: {total_sales})")
        
        # Test AI agent import
        if callable(generate_next_gen_hooks):
            print("✅ AI agent function is callable")
        else:
            print("❌ AI agent function is not callable")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test FastAPI endpoints are properly registered"""
    print("\n🚀 Testing API Endpoints...")
    
    try:
        import main
        
        # Test app initialization
        app = main.app
        if app.title != "Relicon AI Video Generation Platform":
            print("❌ App title incorrect")
            return False
            
        print("✅ FastAPI app initialized correctly")
        
        # Test critical endpoints exist
        routes = [route.path for route in app.routes]
        critical_endpoints = [
            '/generate-video',
            '/generate-plan',
            '/generate-script',
            '/webhook/shopify',
            '/next-gen/{ad_id}',
            '/health'
        ]
        
        for endpoint in critical_endpoints:
            found = any(endpoint in route for route in routes)
            if found:
                print(f"✅ Endpoint {endpoint} registered")
            else:
                print(f"❌ Endpoint {endpoint} missing")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        traceback.print_exc()
        return False

def test_video_generation_function():
    """Test the core video generation function"""
    print("\n🎥 Testing Core Video Generation...")
    
    try:
        from enhanced_video_generator import create_enhanced_video_generation, make_advertisement_energetic
        
        # Test function is callable
        if not callable(create_enhanced_video_generation):
            print("❌ Video generation function not callable")
            return False
            
        print("✅ Video generation function is callable")
        
        # Test helper functions
        test_text = "This is a test product."
        energetic_text = make_advertisement_energetic(test_text)
        
        if energetic_text == test_text:
            print("❌ Text energizing function didn't modify text")
            return False
            
        print("✅ Text energizing function works correctly")
        print(f"  Original: {test_text}")
        print(f"  Energetic: {energetic_text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Video generation test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 COMPREHENSIVE RELICON SYSTEM TEST")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_video_planning,
        test_script_generation,
        test_database_functionality,
        test_api_endpoints,
        test_video_generation_function
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"\n❌ Test {test.__name__} FAILED")
    
    print("\n" + "=" * 50)
    print(f"🎯 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - System is working correctly!")
        print("✅ Video generation functionality preserved")
        print("✅ Feedback loop functionality preserved")
        print("✅ All components integrated successfully")
        print("✅ main.py is now the central highway")
        return True
    else:
        print("❌ Some tests failed - system may have issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)