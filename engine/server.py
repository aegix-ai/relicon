"""
Improved Relicon Ad Generator API Server
Enhanced with reliability, error handling, and performance optimizations
"""

import sys
import os
import asyncio
import signal
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exception_handlers import http_exception_handler
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
import uvicorn
import time
import logging
from collections import defaultdict
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('engine.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("relicon_api")

# Load environment variables
def load_env_file():
    env_path = Path(__file__).parent.parent / '.env.local'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        logger.info(f"Loaded environment from {env_path}")
    else:
        logger.warning(f"Environment file not found: {env_path}")

load_env_file()

# Add engine to path
engine_root = Path(__file__).parent
sys.path.insert(0, str(engine_root))

# Global state
app_state = {
    "job_manager": None,
    "rate_limiter": defaultdict(list),
    "health_status": "starting"
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    try:
        # Startup
        logger.info("Starting Relicon API server...")
        
        # Initialize services
        from backend.core.job_manager import JobManager
        app_state["job_manager"] = JobManager()
        app_state["health_status"] = "healthy"
        
        # Validate API keys
        required_keys = ["OPENAI_API_KEY", "LUMA_API_KEY", "ELEVENLABS_API_KEY"]
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        
        if missing_keys:
            logger.warning(f"Missing API keys: {missing_keys}")
            if not os.getenv("MOCK_MODE", "false").lower() == "true":
                app_state["health_status"] = "degraded"
        
        logger.info("Server startup complete")
        yield
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        app_state["health_status"] = "unhealthy"
        yield
    finally:
        # Shutdown
        logger.info("Shutting down server...")
        if app_state["job_manager"]:
            await app_state["job_manager"].shutdown()

# Initialize FastAPI with lifespan
app = FastAPI(
    title="Relicon Ad Generator API",
    version="2.0.0",
    description="Enhanced AI video generation API",
    lifespan=lifespan
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5000,http://localhost:3000').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    max_age=600,
)

# Rate limiting
def check_rate_limit(client_ip: str, limit: int = 10, window: int = 3600) -> bool:
    """Enhanced rate limiting with sliding window"""
    now = time.time()
    cutoff = now - window
    
    # Clean old requests
    app_state["rate_limiter"][client_ip] = [
        t for t in app_state["rate_limiter"][client_ip] if t > cutoff
    ]
    
    if len(app_state["rate_limiter"][client_ip]) >= limit:
        return False
    
    app_state["rate_limiter"][client_ip].append(now)
    return True

# Request models
class VideoRequest(BaseModel):
    brand_name: str = Field(..., min_length=1, max_length=100)
    brand_description: str = Field(..., min_length=1, max_length=1000)
    product_name: str = Field(default="", max_length=100)
    product_description: str = Field(default="", max_length=1000)
    target_audience: str = Field(default="general audience", max_length=200)
    tone: str = Field(default="friendly", max_length=50)
    duration: int = Field(default=15, ge=10, le=30)
    call_to_action: str = Field(default="Take action now", max_length=100)
    creative_style: str = Field(default="modern", max_length=50)
    product_image_url: Optional[str] = None

    @validator('*', pre=True)
    def sanitize_input(cls, v):
        if isinstance(v, str):
            # Remove dangerous characters
            dangerous = ['<', '>', ';', '&', '|', '`', '$']
            for char in dangerous:
                v = v.replace(char, '')
            return v.strip()
        return v

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "request_id": id(request)}
    )

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
    return await http_exception_handler(request, exc)

# Health check with detailed status
@app.get("/health")
async def health_check():
    """Enhanced health check"""
    status = app_state["health_status"]
    
    # Check services
    services = {
        "job_manager": app_state["job_manager"] is not None,
        "openai_key": bool(os.getenv("OPENAI_API_KEY")),
        "luma_key": bool(os.getenv("LUMA_API_KEY")),
        "elevenlabs_key": bool(os.getenv("ELEVENLABS_API_KEY")),
        "mock_mode": os.getenv("MOCK_MODE", "false").lower() == "true"
    }
    
    return {
        "status": status,
        "timestamp": time.time(),
        "version": "2.0.0",
        "services": services,
        "active_jobs": len(app_state["job_manager"].jobs) if app_state["job_manager"] else 0
    }

# Video generation endpoint
@app.post("/generate")
async def generate_video(
    request: Request,
    video_request: VideoRequest,
    background_tasks: BackgroundTasks
):
    """Enhanced video generation with better error handling"""
    try:
        # Rate limiting
        client_ip = request.client.host if request.client else "unknown"
        if not check_rate_limit(client_ip):
            raise HTTPException(429, "Rate limit exceeded")
        
        # Validate job manager
        if not app_state["job_manager"]:
            raise HTTPException(503, "Service unavailable")
        
        # Create and start job
        job_id = app_state["job_manager"].create_job(video_request.dict())
        background_tasks.add_task(
            app_state["job_manager"].start_generation,
            job_id,
            video_request.dict()
        )
        
        logger.info(f"Started job {job_id} for {client_ip}")
        return {"job_id": job_id, "status": "queued"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(500, "Failed to start generation")

# Job status endpoint
@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get job status with validation"""
    # Validate job ID
    if not job_id or len(job_id) > 100 or any(c in job_id for c in ['..', '/', '\\']):
        raise HTTPException(400, "Invalid job ID")
    
    if not app_state["job_manager"]:
        raise HTTPException(503, "Service unavailable")
    
    status = app_state["job_manager"].get_job_status(job_id)
    if not status:
        raise HTTPException(404, "Job not found")
    
    return status

# Video serving endpoint
@app.get("/video/{filename}")
async def get_video(filename: str):
    """Secure video file serving"""
    # Validate filename
    if not filename or len(filename) > 200 or any(c in filename for c in ['..', '/', '\\']):
        raise HTTPException(400, "Invalid filename")
    
    if not filename.endswith('.mp4'):
        raise HTTPException(400, "Invalid file type")
    
    # Secure path resolution
    try:
        video_path = (Path("outputs") / filename).resolve()
        outputs_dir = Path("outputs").resolve()
        
        if not str(video_path).startswith(str(outputs_dir)):
            raise HTTPException(403, "Access denied")
        
        if not video_path.exists():
            raise HTTPException(404, "Video not found")
        
        return FileResponse(
            video_path,
            media_type="video/mp4",
            headers={"Cache-Control": "public, max-age=3600"}
        )
        
    except Exception as e:
        logger.error(f"Video serving error: {e}")
        raise HTTPException(500, "File access error")

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """System metrics for monitoring"""
    if not app_state["job_manager"]:
        return {"error": "Service unavailable"}
    
    return app_state["job_manager"].get_metrics()

if __name__ == "__main__":
    print("🚀 Starting Enhanced Relicon API Server...")
    
    # Graceful shutdown handler
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
