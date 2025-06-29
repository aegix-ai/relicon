"""
Celery Tasks for ReelForge Video Generation
Distributed asynchronous processing for AI video pipeline
"""
import json
import os
from celery import Celery
from datetime import datetime
import traceback

from agent.core import ReelForgeAgent
from config.settings import settings, logger
from api.deps import get_redis_client
import asyncio

# Initialize Celery
celery_app = Celery(
    "reelforge_workers",
    broker=settings.redis_url,
    backend=settings.redis_result_backend,
    include=['workers.tasks']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.max_job_duration,
    task_soft_time_limit=settings.max_job_duration - 30,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
)


@celery_app.task(name="run_job_async", bind=True)
def run_job_async(self, job_id: str, payload: dict):
    """
    Main task for processing video generation jobs
    
    This task orchestrates the complete AI video generation pipeline:
    1. Initialize ReelForge AI agent
    2. Update job status throughout processing
    3. Handle errors and retries gracefully
    4. Store final results
    """
    try:
        logger.info("Starting video generation job", job_id=job_id)
        
        # Update job status to processing
        asyncio.run(_update_job_status(job_id, "processing", 10, "Initializing AI agent..."))
        
        # Initialize ReelForge agent
        agent = ReelForgeAgent()
        
        # Update status - starting creative planning
        asyncio.run(_update_job_status(job_id, "processing", 20, "Creating comprehensive creative plan..."))
        
        # Execute the complete pipeline
        result = agent.run(job_id=job_id, **payload)
        
        if result.get("success", False):
            # Update status - pipeline completed
            asyncio.run(_update_job_status(job_id, "processing", 90, "Finalizing video output..."))
            
            # Extract video path from result
            video_url = _extract_video_url(result)
            
            # Mark job as completed
            asyncio.run(_update_job_status(
                job_id, 
                "completed", 
                100, 
                "Video generation completed successfully!",
                video_url=video_url,
                completed_at=datetime.utcnow().isoformat()
            ))
            
            logger.info("Job completed successfully", job_id=job_id, video_url=video_url)
            return result
            
        else:
            # Pipeline failed
            error_msg = result.get("error", "Unknown error in video generation")
            logger.error("Job failed", job_id=job_id, error=error_msg)
            
            asyncio.run(_update_job_status(
                job_id,
                "failed",
                0,
                f"Video generation failed: {error_msg}",
                error=error_msg
            ))
            
            return result
            
    except Exception as e:
        error_msg = f"Task execution failed: {str(e)}"
        error_trace = traceback.format_exc()
        
        logger.error("Job execution error", 
                    job_id=job_id, 
                    error=error_msg,
                    traceback=error_trace)
        
        # Update job status to failed
        asyncio.run(_update_job_status(
            job_id,
            "failed", 
            0,
            error_msg,
            error=error_msg
        ))
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info("Retrying job", job_id=job_id, retry_count=self.request.retries + 1)
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        return {
            "success": False,
            "error": error_msg,
            "job_id": job_id,
            "traceback": error_trace if settings.debug else None
        }


@celery_app.task(name="cleanup_old_jobs", bind=True)
def cleanup_old_jobs(self):
    """
    Cleanup task to remove old job data and temporary files
    Runs periodically to prevent storage bloat
    """
    try:
        logger.info("Starting job cleanup task")
        
        # Clean up old output files (older than 24 hours)
        import time
        from pathlib import Path
        
        outputs_dir = Path("outputs")
        current_time = time.time()
        cleanup_threshold = 24 * 3600  # 24 hours in seconds
        
        cleaned_files = 0
        
        for subdir in ["final", "footage", "audio", "temp"]:
            dir_path = outputs_dir / subdir
            if dir_path.exists():
                for file_path in dir_path.iterdir():
                    if file_path.is_file():
                        file_age = current_time - file_path.stat().st_mtime
                        if file_age > cleanup_threshold:
                            try:
                                file_path.unlink()
                                cleaned_files += 1
                                logger.debug("Cleaned up old file", file=str(file_path))
                            except Exception as e:
                                logger.warning("Failed to clean file", file=str(file_path), error=str(e))
        
        logger.info("Job cleanup completed", files_cleaned=cleaned_files)
        return {"files_cleaned": cleaned_files}
        
    except Exception as e:
        logger.error("Cleanup task failed", error=str(e))
        return {"error": str(e)}


@celery_app.task(name="health_check", bind=True)
def health_check(self):
    """
    Health check task to verify worker functionality
    """
    try:
        # Test basic functionality
        test_data = {
            "worker_id": self.request.id,
            "timestamp": datetime.utcnow().isoformat(),
            "settings_loaded": bool(settings.openai_api_key),
            "ffmpeg_available": os.path.exists(settings.ffmpeg_binary_path)
        }
        
        logger.info("Health check passed", **test_data)
        return {"status": "healthy", "details": test_data}
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {"status": "unhealthy", "error": str(e)}


async def _update_job_status(job_id: str, status: str, progress: int, message: str, **kwargs):
    """Update job status in Redis"""
    try:
        redis_client = await get_redis_client()
        
        status_data = {
            "job_id": job_id,
            "status": status,
            "progress": progress,
            "message": message,
            "updated_at": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        # Store in Redis with TTL
        await redis_client.setex(
            f"job:{job_id}",
            3600,  # 1 hour TTL
            json.dumps(status_data)
        )
        
        logger.debug("Job status updated", job_id=job_id, status=status, progress=progress)
        
    except Exception as e:
        logger.error("Failed to update job status", job_id=job_id, error=str(e))


def _extract_video_url(result: dict) -> str:
    """Extract video URL from agent result"""
    try:
        # The result should contain the final video path
        if isinstance(result.get("result"), str):
            # Try to parse as JSON
            try:
                result_data = json.loads(result["result"])
                if "output_file" in result_data:
                    # Convert file path to URL
                    output_file = result_data["output_file"]
                    filename = os.path.basename(output_file)
                    return f"/outputs/final/{filename}"
            except json.JSONDecodeError:
                pass
        
        # Fallback: look for common patterns in result
        result_str = str(result)
        if "outputs/final/" in result_str:
            # Extract filename
            import re
            match = re.search(r'outputs/final/([^"\s]+\.mp4)', result_str)
            if match:
                filename = match.group(1)
                return f"/outputs/final/{filename}"
        
        return None
        
    except Exception as e:
        logger.error("Failed to extract video URL", error=str(e))
        return None


# Configure periodic tasks
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'cleanup-old-jobs': {
        'task': 'cleanup_old_jobs',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
    'health-check': {
        'task': 'health_check', 
        'schedule': 300.0,  # Run every 5 minutes
    },
}

celery_app.conf.timezone = 'UTC'


# Task routing configuration
celery_app.conf.task_routes = {
    'run_job_async': {'queue': 'video_generation'},
    'cleanup_old_jobs': {'queue': 'maintenance'},
    'health_check': {'queue': 'health'}
}

