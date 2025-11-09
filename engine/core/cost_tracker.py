"""
    Cost tracking service for video generation.
    Tracks costs associated with video scenes, audio generation, and planning.
"""

from dataclasses import dataclass


@dataclass
class CostEstimate:
    """Cost estimate breakdown for video generation."""
    video_scenes: int
    video_cost_per_scene: float
    total_video_cost: float
    audio_cost: float
    planning_cost: float
    total_estimated_cost: float
    resolution: str
    duration_seconds: int


class CostTracker:
    """Cost tracking service."""

    # Google Veo pricing (per minute) - currently unused
    VEO_COSTS = {}

    # Luma AI pricing (per 5-second scene) (will be replaced by google veo later)
    LUMA_COSTS = {
        "720p": 0.40,   # $0.40 per 5s 720p scene
        "1080p": 0.90,  # $0.90 per 5s 1080p scene
        "4K": 2.00      # $2.00 per 5s 4K scene
    }

    # OpenAI GPT-4o cost per request
    OPENAI_COST_PER_REQUEST = 0.15

    # ElevenLabs TTS cost per audio & music generation
    ELEVENLABS_COST_PER_AUDIO = 0.05

    def estimate_video_cost(self, scene_count: int = 3, resolution: str = "720p",
                          duration: int = 18) -> CostEstimate:
        """
        Calculate cost estimate for video generation.

        Args:
            scene_count: Number of video scenes to generate
            resolution: Video resolution (720p, 1080p, 4K)
            duration: Total video duration in seconds

        Returns:
            Detailed cost breakdown
        """
        cost_per_scene = self.LUMA_COSTS.get(resolution, self.LUMA_COSTS["720p"])
        total_video_cost = scene_count * cost_per_scene
        audio_cost = self.ELEVENLABS_COST_PER_AUDIO
        planning_cost = self.OPENAI_COST_PER_REQUEST
        total_cost = total_video_cost + audio_cost + planning_cost

        return CostEstimate(
            video_scenes=scene_count,
            video_cost_per_scene=cost_per_scene,
            total_video_cost=total_video_cost,
            audio_cost=audio_cost,
            planning_cost=planning_cost,
            total_estimated_cost=total_cost,
            resolution=resolution,
            duration_seconds=duration
        )


# Global cost tracker instance
cost_tracker = CostTracker()
