#!/usr/bin/env python3
"""
Simplified ReelForge Server
Run this to start the video generation API
"""
import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uuid
import json
from datetime import datetime

# Ensure OpenAI API key is available
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable is required")
    sys.exit(1)

app = FastAPI(
    title="ReelForge AI Video Generator",
    description="Autonomous AI-powered video ad generation platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for job status
job_storage = {}

# Pydantic models
class GenerateRequest(BaseModel):
    brand_name: str = Field(..., description="Name of the brand/product")
    brand_description: str = Field(..., description="Detailed description")
    target_audience: Optional[str] = Field(None, description="Target audience")
    tone: Optional[str] = Field("professional", description="Tone of the ad")
    duration: Optional[int] = Field(30, ge=15, le=60, description="Duration in seconds")
    call_to_action: Optional[str] = Field(None, description="Call-to-action text")
    custom_requirements: Optional[str] = Field(None, description="Custom requirements")

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int = Field(ge=0, le=100)
    message: str
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    video_url: Optional[str] = None
    error: Optional[str] = None

async def update_job_status(job_id: str, status: str, progress: int, message: str, **kwargs):
    """Update job status in memory"""
    job_storage[job_id] = {
        "job_id": job_id,
        "status": status,
        "progress": progress,
        "message": message,
        "updated_at": datetime.now().isoformat(),
        **kwargs
    }

async def mock_video_generation(job_id: str, request_data: dict):
    """Mock video generation process for demonstration"""
    try:
        # Simulate the AI video generation pipeline stages
        stages = [
            (20, "Generating creative concept..."),
            (40, "Writing script segments..."),
            (60, "Creating timeline and effects..."),
            (80, "Generating voiceover audio..."),
            (90, "Sourcing stock footage..."),
            (100, "Assembling final video...")
        ]
        
        for progress, message in stages:
            await update_job_status(job_id, "processing", progress, message)
            # In real implementation, actual AI processing would happen here
            
        # Mark as completed with mock video URL
        await update_job_status(
            job_id,
            "completed", 
            100,
            "Video generation completed successfully!",
            video_url=f"/assets/{job_id}_final.mp4",
            completed_at=datetime.now().isoformat(),
            metadata={
                "brand_name": request_data.get("brand_name"),
                "duration": request_data.get("duration", 30),
                "concept": "Revolutionary AI-generated concept",
                "style": "Professional with dynamic transitions"
            }
        )
        
    except Exception as e:
        await update_job_status(
            job_id,
            "failed",
            0,
            f"Video generation failed: {str(e)}"
        )

@app.get("/")
async def root():
    """Main page"""
    return {
        "message": "ReelForge AI Video Generator",
        "status": "running",
        "version": "1.0.0",
        "description": "Autonomous AI-powered video ad generation"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }

@app.post("/api/generate", response_model=JobResponse)
async def generate_ad(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Generate a video ad"""
    job_id = str(uuid.uuid4())
    
    # Store initial job status
    await update_job_status(
        job_id,
        "queued",
        0,
        "Job queued for processing",
        created_at=datetime.now().isoformat()
    )
    
    # Add background task for video generation
    background_tasks.add_task(mock_video_generation, job_id, request.dict())
    
    return JobResponse(
        job_id=job_id,
        status="queued",
        message="Video generation job has been queued"
    )

@app.get("/api/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get job status"""
    job_data = job_storage.get(job_id)
    
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatus(**job_data)

@app.get("/api/jobs")
async def list_jobs():
    """List all jobs"""
    jobs = [
        {"job_id": job_id, "status": job_data.get("status", "unknown")}
        for job_id, job_data in job_storage.items()
    ]
    return {"jobs": jobs}

# Serve static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

if os.path.exists("assets"):
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")

@app.get("/interface")
async def serve_interface():
    """Serve the HTML interface"""
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")

if __name__ == "__main__":
    print("🎬 Starting ReelForge AI Video Generator")
    print("📡 API will be available at: http://localhost:8000")
    print("🌐 Web interface at: http://localhost:8000/interface")
    print("📚 API docs at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        log_level="info",
        reload=False
    )