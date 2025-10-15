#!/usr/bin/env python3
"""
  Test script to demonstrate the new structured JSON logging format.
  Run this to see the enterprise-grade logging in action.
"""

import sys
import os
from pathlib import Path

# Add relicon to path
sys.path.append(str(Path(__file__).parent))

from core.logger import (
    get_logger, 
    set_trace_context,
    video_logger,
    audio_logger,
    orchestrator_logger,
    assembly_logger
)

def test_structured_logging():
    """Demonstrate the structured JSON logging system."""
    
    # Set trace context
    set_trace_context("test_trace_123", "test_txn_456")
    
    # Test basic logger
    test_logger = get_logger("test_module")
    test_logger.info("Testing structured logging system", "test.start")
    
    # Test domain-specific logging methods
    print("\n=== Video Generation Logging ===")
    video_logger.video_generation_start("job_123", "Hailuo", 150)
    video_logger.video_generation_complete("job_123", 18.5, 1.45, "/outputs/video.mp4")
    
    print("\n=== Audio Processing Logging ===") 
    audio_logger.audio_processing_start("job_123", "ElevenLabs", "ElevenLabs")
    audio_logger.audio_mixing_complete("job_123", -12.3, -25.7, 18.0)
    
    print("\n=== Cost Tracking Logging ===")
    cost_breakdown = {"video": 1.20, "audio": 0.25, "planning": 0.05}
    orchestrator_logger.cost_tracking_update("job_123", 1.50, cost_breakdown)
    
    print("\n=== Job Progress Logging ===")
    orchestrator_logger.job_progress_update("job_123", 85, "processing", "audio_mixing")
    
    print("\n=== Assembly Timing Debug ===")
    assembly_logger.assembly_timing_debug("job_123", 18.0, 17.8, True)
    
    print("\n=== Error Logging ===")
    audio_logger.error("Failed to generate background music", "audio.music.generation.failed", 
                      **{"audio.provider": "ElevenLabs", "audio.error_code": "quota_exceeded"})
    
    print("\n=== Warning Logging ===")
    video_logger.warning("Video generation took longer than expected", "video.performance.warning",
                        **{"video.expected_time_s": 120, "video.actual_time_s": 180})
    
    test_logger.info("Structured logging test completed", "test.complete")

if __name__ == "__main__":
    print("Testing Relicon Structured JSON Logging System")
    print("=" * 60)
    test_structured_logging()
    print("=" * 60)
    print("All logs above are single-line JSON objects suitable for:")
    print("   • Machine parsing (JSON structured)")
    print("   • Terminal tailing (single-line streaming)")
    print("   • Log aggregation systems (ECS compliant)")
    print("   • Trace correlation (trace.id and transaction.id)")
