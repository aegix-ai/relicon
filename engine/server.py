"""
Relicon Ad Generator API Server
FastAPI backend for the Relicon Creative Studio
"""

import sys
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

# Add engine directory to path
engine_root = Path(__file__).parent
sys.path.insert(0, str(engine_root))

from backend.core.job_manager import JobManager
from core.cost_tracker import cost_tracker
from core.logger import get_logger

# Initialize logger
api_logger = get_logger("api_server")

# Initialize FastAPI app
app = FastAPI(title="Relicon Ad Generator API", version="1.0.0")

# Add CORS middleware to allow requests from Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize job manager
job_manager = JobManager()

class VideoRequest(BaseModel):
    brand_name: str
    brand_description: str
    product_name: str = ""
    product_description: str = ""
    target_audience: str = "general audience"
    tone: str = "friendly"
    duration: int = 18
    call_to_action: str = "Take action now"
    creative_style: str = "modern"

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    cost_estimate = cost_tracker.estimate_video_cost()
    return {
        "status": "running",
        "version": "1.0.0",
        "pricing": {
            "estimated_cost_per_video": f"${cost_estimate.total_estimated_cost:.2f}",
            "resolution": cost_estimate.resolution,
        }
    }

@app.post("/generate")
async def generate_video(request: VideoRequest):
    """Generate video ad"""
    try:
        request_data = {
            "brand_name": request.brand_name,
            "brand_description": request.brand_description,
            "product_name": request.product_name,
            "product_description": request.product_description,
            "target_audience": request.target_audience,
            "tone": request.tone,
            "duration": request.duration,
            "call_to_action": request.call_to_action,
            "creative_style": request.creative_style
        }
        
        job_id = job_manager.create_job(request_data)
        job_manager.start_generation(job_id, request_data)
        
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Video generation started"
        }
        
    except Exception as e:
        api_logger.error(f"Generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and progress"""
    status = job_manager.get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status

@app.get("/video/{filename}")
async def get_video(filename: str):
    """Serve generated video files"""
    video_path = Path(__file__).parent / "outputs" / filename
    if video_path.exists():
        return FileResponse(video_path, media_type="video/mp4")
    raise HTTPException(status_code=404, detail="Video not found")

# Ensure outputs directory exists
outputs_dir = Path(__file__).parent / "outputs"
outputs_dir.mkdir(exist_ok=True)

if __name__ == "__main__":
    print("Starting Relicon Ad Generator API Server on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
