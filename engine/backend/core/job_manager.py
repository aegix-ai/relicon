"""
Improved Job Manager with enhanced reliability and performance
"""

import asyncio
import time
import threading
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import logging
from collections import defaultdict
import json

from core.orchestrator import VideoOrchestrator
from core.logger import get_logger

logger = get_logger("job_manager_improved")

class JobManager:
    """Enhanced job manager with reliability and performance improvements"""
    
    def __init__(self, max_workers: int = 3):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.orchestrator = VideoOrchestrator()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.max_workers = max_workers
        self.active_jobs = 0
        self.job_lock = threading.Lock()
        
        # Metrics
        self.metrics = {
            "total_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "average_duration": 0,
            "start_time": time.time()
        }
        
        # Start cleanup task
        self._start_cleanup_task()
        logger.info(f"Enhanced job manager initialized with {max_workers} workers")
    
    def create_job(self, request_data: Dict[str, Any]) -> str:
        """Create job with enhanced validation and tracking"""
        import random
        import string
        
        timestamp = int(time.time())
        job_id = f"job_{timestamp}_{''.join(random.choices(string.hexdigits[:16], k=8))}"
        
        with self.job_lock:
            self.jobs[job_id] = {
                "job_id": job_id,
                "status": "queued",
                "progress": 0,
                "message": "Job queued",
                "created_at": datetime.utcnow().isoformat(),
                "started_at": None,
                "completed_at": None,
                "video_url": None,
                "request_data": request_data,
                "retry_count": 0,
                "error_details": None,
                "estimated_completion": None
            }
            
            self.metrics["total_jobs"] += 1
        
        logger.info(f"Created job {job_id}")
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status with additional metadata"""
        with self.job_lock:
            job = self.jobs.get(job_id)
            if not job:
                return None
            
            # Calculate estimated completion time
            estimated_completion = None
            if job["status"] == "processing" and job["started_at"]:
                started = datetime.fromisoformat(job["started_at"])
                elapsed = (datetime.utcnow() - started).total_seconds()
                progress = max(job["progress"], 1)
                
                # Estimate based on current progress
                total_estimated = (elapsed / progress) * 100
                remaining = max(0, total_estimated - elapsed)
                estimated_completion = (datetime.utcnow() + timedelta(seconds=remaining)).isoformat()
            
            return {
                "job_id": job["job_id"],
                "status": job["status"],
                "progress": job["progress"],
                "message": job.get("message", ""),
                "created_at": job["created_at"],
                "started_at": job.get("started_at"),
                "completed_at": job.get("completed_at"),
                "video_url": job.get("video_url"),
                "current_step": job.get("current_step"),
                "estimated_completion": estimated_completion,
                "retry_count": job.get("retry_count", 0),
                "queue_position": self._get_queue_position(job_id)
            }
    
    def _get_queue_position(self, job_id: str) -> int:
        """Calculate position in queue"""
        queued_jobs = [
            job for job in self.jobs.values()
            if job["status"] == "queued"
        ]
        queued_jobs.sort(key=lambda x: x["created_at"])
        
        for i, job in enumerate(queued_jobs):
            if job["job_id"] == job_id:
                return i + 1
        return 0
    
    def update_job(self, job_id: str, updates: Dict[str, Any]):
        """Thread-safe job updates with validation"""
        with self.job_lock:
            if job_id not in self.jobs:
                logger.warning(f"Attempted to update non-existent job: {job_id}")
                return
            
            # Validate progress
            if "progress" in updates:
                progress = max(0, min(100, updates["progress"]))
                updates["progress"] = progress
            
            # Update timestamps
            if updates.get("status") == "processing" and not self.jobs[job_id].get("started_at"):
                updates["started_at"] = datetime.utcnow().isoformat()
            
            if updates.get("status") in ["completed", "failed"]:
                updates["completed_at"] = datetime.utcnow().isoformat()
                
                # Update metrics
                if updates.get("status") == "completed":
                    self.metrics["completed_jobs"] += 1
                elif updates.get("status") == "failed":
                    self.metrics["failed_jobs"] += 1
                
                # Calculate duration for metrics
                if self.jobs[job_id].get("started_at"):
                    started = datetime.fromisoformat(self.jobs[job_id]["started_at"])
                    duration = (datetime.utcnow() - started).total_seconds()
                    
                    # Update average duration
                    completed = self.metrics["completed_jobs"]
                    if completed > 0:
                        current_avg = self.metrics["average_duration"]
                        self.metrics["average_duration"] = (current_avg * (completed - 1) + duration) / completed
            
            self.jobs[job_id].update(updates)
            
            # Log significant updates
            if "status" in updates or "progress" in updates:
                progress = self.jobs[job_id].get("progress", 0)
                status = self.jobs[job_id].get("status", "unknown")
                message = updates.get("message", "")
                logger.info(f"Job {job_id}: {status} ({progress}%) - {message}")
    
    async def start_generation(self, job_id: str, request_data: Dict[str, Any]):
        """Start generation with improved error handling and retries"""
        if self.active_jobs >= self.max_workers:
            logger.warning(f"Job {job_id} queued - max workers ({self.max_workers}) reached")
            return
        
        self.active_jobs += 1
        
        try:
            # Submit to thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self._run_generation_with_retry,
                job_id,
                request_data
            )
        finally:
            self.active_jobs -= 1
    
    def _run_generation_with_retry(self, job_id: str, request_data: Dict[str, Any], max_retries: int = 2):
        """Run generation with retry logic"""
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"Retrying job {job_id} (attempt {attempt + 1})")
                    self.update_job(job_id, {
                        "status": "processing",
                        "progress": 5,
                        "message": f"Retrying generation (attempt {attempt + 1})...",
                        "retry_count": attempt
                    })
                
                self._run_generation(job_id, request_data)
                return  # Success, exit retry loop
                
            except Exception as e:
                logger.error(f"Job {job_id} attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries:
                    # Wait before retry with exponential backoff
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    # Final failure
                    self.update_job(job_id, {
                        "status": "failed",
                        "progress": 0,
                        "message": f"Generation failed after {max_retries + 1} attempts: {str(e)}",
                        "error_details": str(e),
                        "retry_count": attempt
                    })
    
    def _run_generation(self, job_id: str, request_data: Dict[str, Any]):
        """Core generation logic with enhanced progress tracking"""
        try:
            self.update_job(job_id, {
                "status": "processing",
                "progress": 5,
                "message": "Initializing video generation...",
                "current_step": "Initializing"
            })
            
            # Enhanced progress callback with step tracking
            def progress_callback(progress: int, message: str):
                # Map progress to steps for better UX
                step_mapping = {
                    (0, 20): "Planning",
                    (20, 40): "Generating script",
                    (40, 70): "Creating video scenes",
                    (70, 90): "Adding audio",
                    (90, 100): "Finalizing"
                }
                
                current_step = "Processing"
                for (start, end), step in step_mapping.items():
                    if start <= progress < end:
                        current_step = step
                        break
                
                self.update_job(job_id, {
                    "progress": progress,
                    "message": message,
                    "current_step": current_step
                })
            
            # Generate video
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
                progress_callback=progress_callback
            )
            
            if video_path:
                import os
                filename = os.path.basename(video_path)
                self.update_job(job_id, {
                    "status": "completed",
                    "progress": 100,
                    "message": "Video generation completed successfully!",
                    "current_step": "Completed",
                    "video_url": f"/api/engine/video/{filename}"
                })
                logger.info(f"Job {job_id} completed: {filename}")
            else:
                raise Exception("No output file created")
                
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            raise
    
    def _start_cleanup_task(self):
        """Start background cleanup of old jobs"""
        def cleanup_old_jobs():
            while True:
                try:
                    cutoff = datetime.utcnow() - timedelta(hours=24)
                    
                    with self.job_lock:
                        old_jobs = [
                            job_id for job_id, job in self.jobs.items()
                            if datetime.fromisoformat(job["created_at"]) < cutoff
                            and job["status"] in ["completed", "failed"]
                        ]
                        
                        for job_id in old_jobs:
                            del self.jobs[job_id]
                        
                        if old_jobs:
                            logger.info(f"Cleaned up {len(old_jobs)} old jobs")
                    
                    time.sleep(3600)  # Run every hour
                    
                except Exception as e:
                    logger.error(f"Cleanup task error: {e}")
                    time.sleep(3600)
        
        cleanup_thread = threading.Thread(target=cleanup_old_jobs, daemon=True)
        cleanup_thread.start()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        uptime = time.time() - self.metrics["start_time"]
        
        with self.job_lock:
            active_jobs = len([j for j in self.jobs.values() if j["status"] == "processing"])
            queued_jobs = len([j for j in self.jobs.values() if j["status"] == "queued"])
        
        return {
            "uptime_seconds": uptime,
            "total_jobs": self.metrics["total_jobs"],
            "completed_jobs": self.metrics["completed_jobs"],
            "failed_jobs": self.metrics["failed_jobs"],
            "active_jobs": active_jobs,
            "queued_jobs": queued_jobs,
            "average_duration_seconds": self.metrics["average_duration"],
            "success_rate": (
                self.metrics["completed_jobs"] / max(1, self.metrics["total_jobs"])
            ) * 100,
            "worker_utilization": (active_jobs / self.max_workers) * 100
        }
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down job manager...")
        self.executor.shutdown(wait=True)
        logger.info("Job manager shutdown complete")
