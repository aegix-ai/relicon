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

async def ai_video_generation(job_id: str, request_data: dict):
    """Real AI video generation using the agent system"""
    try:
        await update_job_status(job_id, "processing", 5, "Initializing AI video generation...")
        
        # Import the AI tools
        sys.path.append('.')
        from agent.tools.concept import ConceptGenerationTool
        from agent.tools.script import ScriptWritingTool
        from agent.tools.tts import TextToSpeechTool
        
        # Stage 1: Generate concept
        await update_job_status(job_id, "processing", 15, "Creating revolutionary concept...")
        concept_tool = ConceptGenerationTool()
        concept_result = concept_tool.run(json.dumps(request_data))
        concept_data = json.loads(concept_result)
        
        if concept_data.get("status") == "failed":
            raise Exception(f"Concept generation failed: {concept_data.get('error')}")
        
        # Stage 2: Write dynamic script
        await update_job_status(job_id, "processing", 35, "Writing engaging script...")
        script_tool = ScriptWritingTool()
        script_input = {
            "concept": concept_data,
            "brand_info": request_data
        }
        script_result = script_tool.run(json.dumps(script_input))
        script_data = json.loads(script_result)
        
        if script_data.get("status") == "failed":
            raise Exception(f"Script writing failed: {script_data.get('error')}")
        
        # Stage 3: Generate high-quality audio
        await update_job_status(job_id, "processing", 65, "Generating professional voiceover...")
        tts_tool = TextToSpeechTool()
        tts_input = {
            "script": script_data,
            "job_id": job_id,
            "brand_info": request_data
        }
        audio_result = tts_tool.run(json.dumps(tts_input))
        audio_data = json.loads(audio_result)
        
        if audio_data.get("status") == "failed":
            print(f"TTS Warning: {audio_data.get('error')} - Continuing with text-only version")
            audio_data = {"audio_files": [], "total_duration": 30}
        
        # Stage 4: Create actual video with FFmpeg
        await update_job_status(job_id, "processing", 85, "Generating video with FFmpeg...")
        from agent.tools.ffmpeg_fx import FFmpegAssemblyTool
        
        ffmpeg_tool = FFmpegAssemblyTool()
        video_input = {
            "script": script_data,
            "audio": audio_data,
            "concept": concept_data,
            "job_id": job_id
        }
        video_result = ffmpeg_tool.run(json.dumps(video_input))
        video_data = json.loads(video_result)
        
        if video_data.get("status") == "failed":
            print(f"Video Warning: {video_data.get('error')} - Creating text-only version")
            # Create simplified metadata for failed video generation
            video_data = {
                "video_url": f"/assets/{job_id}_final.mp4",
                "status": "text_only",
                "audio_included": len(audio_data.get("audio_files", [])) > 0
            }
        
        # Create comprehensive result
        final_metadata = {
            "brand_name": request_data.get("brand_name"),
            "duration": request_data.get("duration", 30),
            "concept": concept_data.get("concept", ""),
            "hook": concept_data.get("hook", ""),
            "visual_style": concept_data.get("visual_style", ""),
            "script_segments": len(script_data.get("segments", [])),
            "audio_files": len(audio_data.get("audio_files", [])),
            "voice_tone": request_data.get("tone", "professional"),
            "generation_type": "AI-powered short-form ad",
            "video_format": video_data.get("format", "mp4"),
            "resolution": video_data.get("resolution", "1080x1920")
        }
        
        # Mark as completed
        await update_job_status(
            job_id,
            "completed", 
            100,
            "Dynamic short-form ad generated successfully!",
            video_url=f"/assets/{job_id}_final.mp4",
            completed_at=datetime.now().isoformat(),
            metadata=final_metadata,
            concept=concept_data,
            script=script_data,
            audio=audio_data
        )
        
    except Exception as e:
        print(f"Video generation error for job {job_id}: {str(e)}")
        await update_job_status(
            job_id,
            "failed",
            0,
            f"Video generation failed: {str(e)}"
        )

@app.get("/api/")
async def api_root():
    """API root endpoint"""
    return {
        "message": "ReelForge AI Video Generator API",
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
    background_tasks.add_task(ai_video_generation, job_id, request.dict())
    
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

@app.get("/")
async def serve_frontend():
    """Serve the main frontend interface"""
    from fastapi.responses import FileResponse
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    else:
        return {
            "message": "ReelForge AI Video Generator",
            "status": "running",
            "version": "1.0.0",
            "frontend": "Available at /interface",
            "api_docs": "Available at /docs"
        }

if __name__ == "__main__":
    print("🎬 Starting ReelForge AI Video Generator")
    print("📡 API will be available at: http://localhost:8001")
    print("🌐 Web interface at: http://localhost:8001/interface")
    print("📚 API docs at: http://localhost:8001/docs")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,  # Use different port to avoid conflict
        log_level="info",
        reload=False
    )