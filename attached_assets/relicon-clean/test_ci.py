#!/usr/bin/env python3
"""
  CI/CD test script for GitHub Actions.
  Tests core functionality without requiring external API keys.
  Root-level version for GitHub repository structure.
"""

import sys
import os
from pathlib import Path

# Add current directory to path for root-level repository structure
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test that all core modules can be imported."""
    print("Testing core module imports...")
    
    try:
        from core.orchestrator import VideoOrchestrator
        from core.planning_service import PlanningService  
        from core.video_service import VideoService
        from core.audio_service import AudioService
        from core.assembly_service import AssemblyService
        from core.cost_tracker import cost_tracker
        from core.logger import get_logger
        
        from providers.openai import OpenAIProvider
        from providers.elevenlabs import ElevenLabsProvider
        from providers.hailuo import HailuoProvider
        from providers.luma import LumaProvider
        
        from backend.core.job_manager import JobManager
        from config.settings import settings
        
        print("All core modules imported successfully")
        return True
    except Exception as e:
        print(f"Import failed: {e}")
        return False

def test_cost_tracker():
    """Test cost estimation functionality."""
    print("Testing cost tracker...")
    
    try:
        from core.cost_tracker import cost_tracker
        
        # Test cost estimation
        estimate = cost_tracker.estimate_video_cost()
        assert estimate.total_estimated_cost > 0, "Cost should be positive"
        assert estimate.resolution == "720p", "Should default to 720p"
        
        # Test budget validation
        budget_check = cost_tracker.validate_budget(1.5)
        assert "within_budget" in budget_check, "Budget check should return status"
        
        print(f"Cost estimation working: ${estimate.total_estimated_cost:.2f}")
        return True
    except Exception as e:
        print(f"Cost tracker test failed: {e}")
        return False

def test_structured_logging():
    """Test structured logging system."""
    print("Testing structured logging...")
    
    try:
        from core.logger import get_logger, set_trace_context
        
        # Set trace context
        set_trace_context("ci_test_123", "ci_txn_456")
        
        # Test logger creation
        logger = get_logger("ci_test")
        
        # Test logging methods
        logger.info("CI test log entry", "ci.test.info")
        logger.warning("CI test warning", "ci.test.warning", **{"test.param": "value"})
        
        print("Structured logging working")
        return True
    except Exception as e:
        print(f"Structured logging test failed: {e}")
        return False

def test_job_manager():
    """Test job management system."""
    print("Testing job manager...")
    
    try:
        from backend.core.job_manager import JobManager
        
        job_manager = JobManager()
        
        # Test job creation
        job_id = job_manager.create_job({
            "brand_name": "Test Brand",
            "brand_description": "Test description"
        })
        
        assert job_id is not None, "Job ID should be created"
        
        # Test job status
        status = job_manager.get_job_status(job_id)
        assert status is not None, "Job status should be available"
        
        print(f"Job manager working: created job {job_id}")
        return True
    except Exception as e:
        print(f"Job manager test failed: {e}")
        return False

def test_settings():
    """Test configuration settings."""
    print("Testing settings configuration...")
    
    try:
        from config.settings import settings
        
        # Test settings attributes that actually exist  
        assert hasattr(settings, 'OUTPUT_DIR'), "Output directory should be configured"
        assert hasattr(settings, 'MAX_CONCURRENT_JOBS'), "Max concurrent jobs should be configured"
        assert settings.MAX_CONCURRENT_JOBS > 0, "Max concurrent jobs should be positive"
        
        print(f"Settings loaded: output_dir={settings.OUTPUT_DIR}, max_jobs={settings.MAX_CONCURRENT_JOBS}")
        return True
    except Exception as e:
        print(f"Settings test failed: {e}")
        return False

def main():
    """Run all CI tests."""
    print("Running Relicon CI Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_cost_tracker,
        test_structured_logging,
        test_job_manager,
        test_settings
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Test {test.__name__} crashed: {e}")
            failed += 1
        print("-" * 30)
    
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("All tests passed! Relicon is ready for deployment.")
        return 0
    else:
        print("Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
