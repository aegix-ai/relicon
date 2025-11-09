"""
  Core video generation pipeline.

  Simple, focused architecture:
  - Pipeline: LangGraph-based orchestrator (plan → video → audio → assemble)
  - Services: Direct service implementations (no wrappers)
  - Utilities: Cost tracking, logging, provider management
"""

# Main pipeline
from core.pipeline import VideoGenerationPipeline, pipeline

# Core services (for direct access if needed)
from core.video_planner import PlanningService
from core.video_generator import VideoService
from core.audio_orchestrator import AudioService
from core.video_assembler import AssemblyService

# Utilities
from core.cost_tracker import CostTracker, cost_tracker
from core.provider_manager import ProviderManager, provider_manager
from core.logger import get_logger

__all__ = [
    # Main API
    "VideoGenerationPipeline",
    "pipeline",

    # Services (for advanced usage)
    "PlanningService",
    "VideoService",
    "AudioService",
    "AssemblyService",

    # Utilities
    "CostTracker",
    "cost_tracker",
    "ProviderManager",
    "provider_manager",
    "get_logger",
]