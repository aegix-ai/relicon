"""
  Job Manager for Enterprise Relicon System
  Handles video generation job tracking and status updates
"""

import uuid
import time
import threading
import sys
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

@dataclass 
class JobStatus:
    job_id: str
    status: str
    progress: int
    message: str
    created_at: str
    completed_at: Optional[str] = None
    video_url: Optional[str] = None
    
class JobManager:
    """Enterprise job management system"""
    
    def __init__(self):
        self.jobs: Dict[str, JobStatus] = {}
        print("Enterprise Relicon job manager initialized")
    
    def create_job(self, request_data: Dict[str, Any]) -> str:
        """Create a new video generation job"""
        job_id = f"job_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        job_status = JobStatus(
            job_id=job_id,
            status="queued",
            progress=0,
            message="Job created successfully",
            created_at=datetime.now().isoformat()
        )
        
        self.jobs[job_id] = job_status
        print(f"Created job {job_id}")
        return job_id
    
    def update_job_status(self, job_id: str, status: str, progress: int, message: str, **extras):
        """Update job status"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.status = status
            job.progress = progress
            job.message = message
            
            if status == "completed":
                job.completed_at = datetime.now().isoformat()
                
            for key, value in extras.items():
                setattr(job, key, value)
                
            print(f"Job {job_id}: {status} ({progress}%) - {message}")
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status"""
        if job_id in self.jobs:
            return asdict(self.jobs[job_id])
        return None
    
    def start_generation(self, job_id: str, brand_info: dict = None):
        """Start video generation process using enterprise orchestrator"""
        self.update_job_status(job_id, "processing", 5, "Initializing enterprise video generation...")
        
        def real_generation():
            try:
                # Import the enterprise orchestrator
                relicon_root = Path(__file__).parent.parent.parent
                sys.path.insert(0, str(relicon_root))
                
                from core.orchestrator import VideoOrchestrator
                
                # Create output path
                output_filename = f"{job_id}.mp4"
                output_path = f"outputs/{output_filename}"
                
                # Initialize orchestrator
                orchestrator = VideoOrchestrator()
                
                # Update status
                self.update_job_status(job_id, "processing", 10, "Creating video architecture...")
                
                # Progress callback to update job status in real-time
                def progress_callback(progress: int, message: str):
                    self.update_job_status(job_id, "processing", progress, message)
                
                # Generate video using enterprise system
                result = orchestrator.create_complete_video(brand_info, output_path, progress_callback)
                
                if result['success']:
                    # Video generated successfully
                    self.update_job_status(
                        job_id, "completed", 100, 
                        f"Video generated successfully in {result['duration']:.1f}s",
                        video_url=f"/api/engine/video/{job_id}.mp4"
                    )
                else:
                    # Generation failed
                    self.update_job_status(
                        job_id, "failed", 0, 
                        f"Video generation failed: {result.get('error', 'Unknown error')}"
                    )
                    
            except Exception as e:
                print(f"Generation error for job {job_id}: {e}")
                self.update_job_status(
                    job_id, "failed", 0, 
                    f"Generation failed: {str(e)}"
                )
        
        # Start generation in background thread
        thread = threading.Thread(target=real_generation, daemon=True)
        thread.start()
