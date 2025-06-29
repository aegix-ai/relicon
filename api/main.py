"""
ReelForge FastAPI Application
Microkernel architecture for autonomous video ad generation
"""
from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from uuid import uuid4
import os
from typing import Dict, Any
import aiofiles

from .schemas import GenerateRequest, JobStatus, JobResponse
from .deps import get_redis_client
from workers.tasks import run_job_async
from config.settings import settings, logger

app = FastAPI(
    title="ReelForge AI Video Generator",
    description="Autonomous AI engine for creating unique short-form video ads",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory job tracking (in production, use Redis)
job_store: Dict[str, Dict[str, Any]] = {}


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main frontend interface"""
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>ReelForge API</h1><p>Frontend not found. Use /docs for API documentation.</p>")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_client = get_redis_client()
        await redis_client.ping()
        return {
            "status": "healthy",
            "services": {
                "api": "up",
                "redis": "up",
                "ffmpeg": os.path.exists(settings.ffmpeg_binary_path)
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.post("/api/generate", response_model=JobResponse)
async def generate_ad(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Generate a video ad based on brand information
    Returns job ID for tracking progress
    """
    job_id = str(uuid4())
    
    # Initialize job status
    job_store[job_id] = {
        "status": "queued",
        "progress": 0,
        "message": "Job queued for processing",
        "created_at": None,
        "video_url": None,
        "error": None
    }
    
    # Queue the job
    background_tasks.add_task(run_job_async, job_id, request.dict())
    
    logger.info("Job queued", job_id=job_id, brand=request.brand_name)
    
    return JobResponse(
        job_id=job_id,
        status="queued",
        message="Video generation job queued successfully"
    )


@app.get("/api/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get the status of a video generation job"""
    try:
        redis_client = get_redis_client()
        
        # Try to get status from Redis first
        redis_status = await redis_client.get(f"job:{job_id}")
        if redis_status:
            import json
            status_data = json.loads(redis_status)
            return JobStatus(**status_data)
        
        # Fallback to in-memory store
        if job_id not in job_store:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JobStatus(job_id=job_id, **job_store[job_id])
    
    except Exception as e:
        logger.error("Failed to get job status", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve job status")


@app.post("/api/assets")
async def upload_asset(file: UploadFile = File(...)):
    """Upload brand assets (logos, product images, etc.)"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Validate file type
    allowed_types = {".jpg", ".jpeg", ".png", ".mp4", ".mov", ".wav", ".mp3"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_ext} not allowed. Allowed types: {allowed_types}"
        )
    
    # Generate unique filename
    asset_id = str(uuid4())
    filename = f"{asset_id}{file_ext}"
    filepath = f"assets/{filename}"
    
    try:
        # Save file
        async with aiofiles.open(filepath, "wb") as f:
            content = await file.read()
            await f.write(content)
        
        logger.info("Asset uploaded", filename=filename, size=len(content))
        
        return {
            "asset_id": asset_id,
            "filename": filename,
            "url": f"/assets/{filename}",
            "size": len(content)
        }
    
    except Exception as e:
        logger.error("Failed to upload asset", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to upload asset")


@app.get("/api/jobs")
async def list_jobs():
    """List all jobs (development endpoint)"""
    if not settings.debug:
        raise HTTPException(status_code=404, detail="Not found")
    
    return {"jobs": list(job_store.keys())}


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
