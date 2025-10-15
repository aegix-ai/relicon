"""
  Cost tracking and optimization service for enterprise video generation.
  Provides real-time cost estimates and prevents budget overruns.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import json


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
    """Real-time cost tracking and optimization service."""
    
    # Luma AI pricing (per 5-second scene)
    LUMA_COSTS = {
        "720p": 0.40,   # $0.40 per 5s 720p scene
        "1080p": 0.90,  # $0.90 per 5s 1080p scene (2.25x more expensive)
        "4K": 2.00      # $2.00 per 5s 4K scene (not recommended)
    }
    
    # Other service costs
    OPENAI_COST_PER_REQUEST = 0.15  # GPT-4o planning cost
    ELEVENLABS_COST_PER_AUDIO = 0.05  # TTS generation cost
    HAILUO_COST_PER_SCENE = 0.45  # MiniMax alternative cost
    
    def __init__(self):
        self.cost_history: List[Dict[str, Any]] = []
    
    def estimate_video_cost(self, scene_count: int = 3, resolution: str = "720p", 
                          duration: int = 18) -> CostEstimate:
        """
        Calculate detailed cost estimate for video generation.
        
        Args:
            scene_count: Number of video scenes to generate
            resolution: Video resolution (720p, 1080p, 4K)
            duration: Total video duration in seconds
            
        Returns:
            Detailed cost breakdown
        """
        # Video generation costs
        cost_per_scene = self.LUMA_COSTS.get(resolution, self.LUMA_COSTS["720p"])
        total_video_cost = scene_count * cost_per_scene
        
        # Audio and planning costs
        audio_cost = self.ELEVENLABS_COST_PER_AUDIO
        planning_cost = self.OPENAI_COST_PER_REQUEST
        
        # Total cost calculation
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
    
    def get_cost_optimization_recommendations(self, current_resolution: str = "1080p") -> Dict[str, Any]:
        """
        Provide cost optimization recommendations.
        
        Args:
            current_resolution: Current video resolution setting
            
        Returns:
            Optimization recommendations with potential savings
        """
        current_estimate = self.estimate_video_cost(resolution=current_resolution)
        optimized_estimate = self.estimate_video_cost(resolution="720p")
        
        savings = current_estimate.total_estimated_cost - optimized_estimate.total_estimated_cost
        savings_percentage = (savings / current_estimate.total_estimated_cost) * 100
        
        return {
            "current_cost": current_estimate.total_estimated_cost,
            "optimized_cost": optimized_estimate.total_estimated_cost,
            "potential_savings": savings,
            "savings_percentage": savings_percentage,
            "videos_per_20_dollars": {
                "current": int(20 / current_estimate.total_estimated_cost),
                "optimized": int(20 / optimized_estimate.total_estimated_cost)
            },
            "recommendation": {
                "action": "Switch to 720p resolution",
                "reason": f"Save ${savings:.2f} per video ({savings_percentage:.1f}% reduction)",
                "quality_impact": "Minimal - 720p is ideal for social media platforms"
            }
        }
    
    def validate_budget(self, estimated_cost: float, max_budget: float = 3.0) -> Dict[str, Any]:
        """
        Validate if generation stays within budget limits.
        
        Args:
            estimated_cost: Estimated cost for the operation
            max_budget: Maximum allowed budget per video
            
        Returns:
            Budget validation result
        """
        within_budget = estimated_cost <= max_budget
        budget_utilization = (estimated_cost / max_budget) * 100
        
        result = {
            "within_budget": within_budget,
            "estimated_cost": estimated_cost,
            "max_budget": max_budget,
            "budget_utilization_percentage": budget_utilization,
            "timestamp": datetime.now().isoformat()
        }
        
        if not within_budget:
            overage = estimated_cost - max_budget
            result["warning"] = f"Cost exceeds budget by ${overage:.2f}"
            result["recommendation"] = "Consider switching to 720p resolution or reducing scenes"
        
        return result
    
    def log_generation_cost(self, job_id: str, actual_cost: float, 
                          scenes_generated: int, resolution: str) -> None:
        """
        Log actual generation costs for analytics.
        
        Args:
            job_id: Unique job identifier
            actual_cost: Actual cost incurred
            scenes_generated: Number of scenes successfully generated
            resolution: Resolution used for generation
        """
        cost_entry = {
            "job_id": job_id,
            "actual_cost": actual_cost,
            "scenes_generated": scenes_generated,
            "resolution": resolution,
            "timestamp": datetime.now().isoformat(),
            "cost_per_scene": actual_cost / scenes_generated if scenes_generated > 0 else 0
        }
        
        self.cost_history.append(cost_entry)
        print(f"Cost logged: {job_id} - ${actual_cost:.2f} ({scenes_generated} scenes @ {resolution})")
    
    def get_cost_analytics(self) -> Dict[str, Any]:
        """
        Generate cost analytics and insights.
        
        Returns:
            Cost analytics dashboard data
        """
        if not self.cost_history:
            return {"message": "No cost data available yet"}
        
        total_costs = [entry["actual_cost"] for entry in self.cost_history]
        average_cost = sum(total_costs) / len(total_costs)
        
        resolution_breakdown = {}
        for entry in self.cost_history:
            res = entry["resolution"]
            if res not in resolution_breakdown:
                resolution_breakdown[res] = {"count": 0, "total_cost": 0}
            resolution_breakdown[res]["count"] += 1
            resolution_breakdown[res]["total_cost"] += entry["actual_cost"]
        
        return {
            "total_videos_generated": len(self.cost_history),
            "total_spend": sum(total_costs),
            "average_cost_per_video": average_cost,
            "videos_per_20_dollars_actual": int(20 / average_cost) if average_cost > 0 else 0,
            "resolution_breakdown": resolution_breakdown,
            "cost_efficiency_score": self._calculate_efficiency_score(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _calculate_efficiency_score(self) -> float:
        """Calculate cost efficiency score (0-100)."""
        if not self.cost_history:
            return 100.0
        
        recent_costs = [entry["actual_cost"] for entry in self.cost_history[-10:]]
        average_recent_cost = sum(recent_costs) / len(recent_costs)
        
        # Score based on how close we are to optimal $1.5 target
        optimal_cost = 1.5
        efficiency = max(0, min(100, (optimal_cost / average_recent_cost) * 100))
        
        return round(efficiency, 1)


# Global cost tracker instance
cost_tracker = CostTracker()
