"""
Job Manager for Relicon Ad Generation
Manages job lifecycle, status tracking, and async generation
"""

import time
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import threading

from core.orchestrator import VideoOrchestrator
from core.logger import get_logger

logger = get_logger("job_manager")


class JobManager:
    """Enterprise job manager for video generation jobs"""
    
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.orchestrator = VideoOrchestrator()
        logger.info("Enterprise Relicon job manager initialized")
    
    def create_job(self, request_data: Dict[str, Any]) -> str:
        """Create a new job"""
        import random
        import string
        
        timestamp = int(time.time())
        job_id = f"job_{timestamp}_{''.join(random.choices(string.hexdigits[:16], k=8))}"
        
        self.jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "progress": 0,
            "message": "Job created",
            "created_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "video_url": None,
            "request_data": request_data
        }
        
        print(f"Created job {job_id}")
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get current job status"""
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        return {
            "job_id": job["job_id"],
            "status": job["status"],
            "progress": job["progress"],
            "message": job.get("message", ""),
            "created_at": job["created_at"],
            "completed_at": job.get("completed_at"),
            "video_url": job.get("video_url"),
            "current_step": job.get("current_step")
        }
    
    def update_job(self, job_id: str, updates: Dict[str, Any]):
        """Update job status"""
        if job_id in self.jobs:
            self.jobs[job_id].update(updates)
            
            progress = updates.get('progress', self.jobs[job_id].get('progress', 0))
            message = updates.get('message', self.jobs[job_id].get('message', ''))
            print(f"Job {job_id}: {updates.get('status', 'processing')} ({progress}%) - {message}")
    
    def start_generation(self, job_id: str, request_data: Dict[str, Any]):
        """Start async video generation"""
        def run_generation():
            try:
                self.update_job(job_id, {
                    "status": "processing",
                    "progress": 5,
                    "message": "Initializing enterprise video generation...",
                    "current_step": "Initializing..."
                })
                
                video_path = self.orchestrator.generate_video_ad(
                    brand_name=request_data.get("brand_name", ""),
                    brand_description=request_data.get("brand_description", ""),
                    product_name=request_data.get("product_name", ""),
                    product_description=request_data.get("product_description", ""),
                    target_audience=request_data.get("target_audience", "general audience"),
                    tone=request_data.get("tone", "professional"),
                    duration=request_data.get("duration", 18),
                    call_to_action=request_data.get("call_to_action", "Learn more"),
                    creative_style=request_data.get("creative_style", "modern"),
                    progress_callback=lambda progress, message, step: self.update_job(job_id, {
                        "progress": progress,
                        "message": message,
                        "current_step": step
                    })
                )
                
                if video_path:
                    import os
                    filename = os.path.basename(video_path)
                    self.update_job(job_id, {
                        "status": "completed",
                        "progress": 100,
                        "message": "Video generation completed successfully!",
                        "completed_at": datetime.utcnow().isoformat(),
                        "video_url": f"/api/engine/video/{filename}"
                    })
                else:
                    raise Exception("Video generation failed: No output file created")
                    
            except Exception as e:
                logger.error(f"Job {job_id} failed: {str(e)}")
                self.update_job(job_id, {
                    "status": "failed",
                    "progress": 0,
                    "message": f"Video generation failed: {str(e)}",
                    "completed_at": datetime.utcnow().isoformat()
                })
        
        thread = threading.Thread(target=run_generation, daemon=True)
        thread.start()
