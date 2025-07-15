"""
Main FastAPI application for Relicon - The Central Highway
Unified entry point for all video generation, AI planning, feedback loops, and task management
"""
import os
import hmac
import hashlib
import json
import tempfile
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import requests
import asyncio
# Configuration using environment variables

# Core Database and AI Agent
from database import get_db, init_db, Sales, Ads
from agent import generate_next_gen_hooks

# Video Generation Pipeline - All Components
from enhanced_video_generator import (
    create_enhanced_video_generation, 
    make_advertisement_energetic,
    enhance_audio_energy,
    progress_update
)
from ai_planner import VideoAdPlanner
from luma_service import LumaVideoService
from dynamic_tree_planner import UltraDynamicTreePlanner
from energetic_script_generator import EnergeticScriptGenerator

# Task Management
from tasks import (
    fetch_meta_metrics,
    fetch_tt_metrics,
    evaluate_creatives
)

# OpenAI Integration
from openai import OpenAI

# Initialize FastAPI app - Central Highway
app = FastAPI(title="Relicon AI Video Generation Platform", version="2.0.0")

# Initialize all services
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
video_planner = VideoAdPlanner()
luma_service = LumaVideoService()
tree_planner = UltraDynamicTreePlanner()
script_generator = EnergeticScriptGenerator()

# Initialize database and all services on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("✓ Database initialized successfully!")
    print("✓ Video generation services initialized!")
    print("✓ AI planning services initialized!")
    print("✓ Task management services initialized!")
    print("🚀 Relicon Central Highway is ready!")


# Data Models for all API endpoints
class ShopifyWebhookData(BaseModel):
    """Shopify webhook data model."""
    id: int
    total_price: str
    customer: Dict[str, Any] = {}
    line_items: list = []
    note_attributes: list = []
    landing_site: str = ""
    referring_site: str = ""

class VideoGenerationRequest(BaseModel):
    """Video generation request model."""
    brand_name: str
    brand_description: str
    target_audience: str = "general audience"
    tone: str = "professional"
    duration: int = 30
    call_to_action: str = "Learn more"
    platform: str = "universal"  # meta, tiktok, universal

class VideoGenerationResponse(BaseModel):
    """Video generation response model."""
    job_id: str
    status: str
    message: str
    video_url: Optional[str] = None
    plan_summary: Optional[Dict[str, Any]] = None

class PlanGenerationRequest(BaseModel):
    """AI planning request model."""
    brand_name: str
    brand_description: str
    target_audience: str = "general audience"
    tone: str = "professional"
    duration: int = 30
    call_to_action: str = "Learn more"
    use_tree_planner: bool = True

class TaskExecutionRequest(BaseModel):
    """Task execution request model."""
    task_type: str  # "collect_metrics", "identify_winners", "generate_hooks"
    platform: Optional[str] = None
    parameters: Dict[str, Any] = {}


def verify_shopify_webhook(request: Request, body: bytes) -> bool:
    """Verify Shopify webhook HMAC signature."""
    try:
        webhook_secret = os.getenv("SHOPIFY_WEBHOOK_SECRET")
        signature = request.headers.get("X-Shopify-Hmac-Sha256")
        
        if not signature:
            return False
            
        expected_signature = hmac.new(
            webhook_secret.encode("utf-8"),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        print(f"Error verifying webhook: {e}")
        return False


# =================== VIDEO GENERATION ENDPOINTS ===================

@app.post("/generate-video", response_model=VideoGenerationResponse)
async def generate_video(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate a complete video using the full AI pipeline.
    This is the main video generation endpoint that orchestrates all services.
    """
    try:
        # Generate unique job ID
        job_id = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create brand info dictionary
        brand_info = {
            "brand_name": request.brand_name,
            "brand_description": request.brand_description,
            "target_audience": request.target_audience,
            "tone": request.tone,
            "duration": request.duration,
            "call_to_action": request.call_to_action,
            "platform": request.platform
        }
        
        # Generate output filename
        output_file = f"outputs/{job_id}.mp4"
        
        # Start video generation in background
        background_tasks.add_task(
            create_enhanced_video_generation,
            brand_info,
            output_file
        )
        
        return VideoGenerationResponse(
            job_id=job_id,
            status="processing",
            message="Video generation started successfully",
            video_url=None,
            plan_summary={"brand_name": request.brand_name, "duration": request.duration}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

@app.post("/generate-plan")
async def generate_plan(request: PlanGenerationRequest):
    """
    Generate AI planning for video content using either standard or tree planner.
    """
    try:
        brand_info = {
            "brand_name": request.brand_name,
            "brand_description": request.brand_description,
            "target_audience": request.target_audience,
            "tone": request.tone,
            "duration": request.duration,
            "call_to_action": request.call_to_action
        }
        
        if request.use_tree_planner:
            # Use revolutionary tree planner
            plan = tree_planner.create_holistic_plan(brand_info)
        else:
            # Use standard video planner
            plan = video_planner.create_complete_plan(brand_info)
        
        return {"status": "success", "plan": plan}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(e)}")

@app.post("/generate-script")
async def generate_script(request: PlanGenerationRequest):
    """
    Generate energetic advertisement script using AI.
    """
    try:
        brand_info = {
            "brand_name": request.brand_name,
            "brand_description": request.brand_description,
            "target_audience": request.target_audience,
            "tone": request.tone,
            "duration": request.duration,
            "call_to_action": request.call_to_action
        }
        
        # Generate script segments
        segments = script_generator.generate_energetic_segments(brand_info, num_segments=3)
        
        return {"status": "success", "script_segments": segments}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Script generation failed: {str(e)}")

@app.post("/execute-task")
async def execute_task(request: TaskExecutionRequest, background_tasks: BackgroundTasks):
    """
    Execute task management functions (metrics collection, winner identification, etc.).
    """
    try:
        if request.task_type == "collect_metrics":
            if request.platform == "meta":
                background_tasks.add_task(fetch_meta_metrics)
            elif request.platform == "tiktok":
                background_tasks.add_task(fetch_tt_metrics)
            else:
                raise HTTPException(status_code=400, detail="Platform required for metrics collection")
                
        elif request.task_type == "evaluate_creatives":
            background_tasks.add_task(evaluate_creatives)
            
        else:
            raise HTTPException(status_code=400, detail="Invalid task type")
        
        return {"status": "success", "message": f"Task {request.task_type} started"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")

# =================== FEEDBACK LOOP ENDPOINTS ===================

@app.post("/webhook/shopify")
async def shopify_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Shopify webhook for order tracking."""
    try:
        body = await request.body()
        
        # Verify HMAC signature
        if not verify_shopify_webhook(request, body):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Parse webhook data
        data = json.loads(body)
        webhook_data = ShopifyWebhookData(**data)
        
        # Extract UTM content from various sources
        utm_content = None
        
        # Check landing site for UTM parameters
        if webhook_data.landing_site and "utm_content=" in webhook_data.landing_site:
            utm_content = webhook_data.landing_site.split("utm_content=")[1].split("&")[0]
        
        # Check note attributes
        for attr in webhook_data.note_attributes:
            if attr.get("name") == "utm_content":
                utm_content = attr.get("value")
                break
        
        # Check referring site
        if not utm_content and webhook_data.referring_site:
            if "utm_content=" in webhook_data.referring_site:
                utm_content = webhook_data.referring_site.split("utm_content=")[1].split("&")[0]
        
        # Create sales record
        sale = Sales(
            order_id=webhook_data.id,
            ad_code=utm_content,
            revenue=float(webhook_data.total_price),
            created_at=datetime.utcnow()
        )
        
        db.add(sale)
        db.commit()
        
        return {"status": "success", "order_id": webhook_data.id, "utm_content": utm_content}
        
    except Exception as e:
        print(f"Error processing Shopify webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")


@app.get("/next-gen/{ad_id}")
async def get_next_gen_hooks(ad_id: str, db: Session = Depends(get_db)):
    """Generate next-generation hooks for an ad using AI agent."""
    try:
        # Get the specific ad
        ad = db.query(Ads).filter(Ads.ad_id == ad_id).first()
        if not ad:
            raise HTTPException(status_code=404, detail="Ad not found")
        
        # Get all winner ads for context
        winner_ads = db.query(Ads).filter(Ads.winner_tag == True).all()
        
        if not winner_ads:
            raise HTTPException(status_code=404, detail="No winning ads found for analysis")
        
        # Generate next-gen hooks using AI agent
        hooks = await generate_next_gen_hooks(winner_ads, ad)
        
        return {
            "status": "success",
            "ad_id": ad_id,
            "next_gen_hooks": hooks,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error generating next-gen hooks: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating hooks: {str(e)}")


@app.get("/analytics/summary")
async def get_analytics_summary(db: Session = Depends(get_db)):
    """Get analytics summary for dashboard."""
    try:
        total_ads = db.query(Ads).count()
        winner_ads = db.query(Ads).filter(Ads.winner_tag == True).count()
        total_sales = db.query(Sales).count()
        
        # Get average ROAS
        avg_roas = db.query(Ads).filter(Ads.roas > 0).with_entities(
            db.func.avg(Ads.roas)
        ).scalar() or 0
        
        return {
            "total_ads": total_ads,
            "winner_ads": winner_ads,
            "total_sales": total_sales,
            "average_roas": float(avg_roas),
            "winner_percentage": (winner_ads / total_ads * 100) if total_ads > 0 else 0
        }
        
    except Exception as e:
        print(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")


@app.get("/video-status/{job_id}")
async def get_video_status(job_id: str):
    """Get status of video generation job."""
    try:
        # Check if video file exists
        video_path = f"outputs/{job_id}.mp4"
        if os.path.exists(video_path):
            return {
                "job_id": job_id,
                "status": "completed",
                "video_url": f"/download-video/{job_id}",
                "message": "Video generation completed successfully"
            }
        else:
            return {
                "job_id": job_id,
                "status": "processing",
                "video_url": None,
                "message": "Video generation in progress"
            }
    except Exception as e:
        return {
            "job_id": job_id,
            "status": "error",
            "video_url": None,
            "message": f"Error checking status: {str(e)}"
        }

@app.get("/download-video/{job_id}")
async def download_video(job_id: str):
    """Download generated video file."""
    try:
        video_path = f"outputs/{job_id}.mp4"
        if os.path.exists(video_path):
            return FileResponse(
                video_path,
                media_type="video/mp4",
                filename=f"{job_id}.mp4"
            )
        else:
            raise HTTPException(status_code=404, detail="Video not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading video: {str(e)}")

@app.get("/luma-status/{job_id}")
async def get_luma_status(job_id: str):
    """Get status of Luma AI video generation job."""
    try:
        status = luma_service.check_generation_status(job_id)
        return {"job_id": job_id, "luma_status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking Luma status: {str(e)}")

# =================== SYSTEM HEALTH & MONITORING ===================

@app.get("/health")
async def health_check():
    """Comprehensive health check for all system components."""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": "healthy",
                "openai": "healthy" if openai_client else "unavailable",
                "luma": "healthy" if luma_service else "unavailable",
                "video_planner": "healthy" if video_planner else "unavailable",
                "tree_planner": "healthy" if tree_planner else "unavailable",
                "script_generator": "healthy" if script_generator else "unavailable"
            },
            "environment": {
                "openai_key": bool(os.environ.get("OPENAI_API_KEY")),
                "luma_key": bool(os.environ.get("LUMA_API_KEY")),
                "elevenlabs_key": bool(os.environ.get("ELEVENLABS_API_KEY")),
                "database_url": bool(os.environ.get("DATABASE_URL"))
            }
        }
        
        return health_status
        
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@app.get("/system-info")
async def get_system_info():
    """Get comprehensive system information and capabilities."""
    return {
        "name": "Relicon AI Video Generation Platform",
        "version": "2.0.0",
        "description": "Unified AI-powered video generation and feedback loop system",
        "capabilities": {
            "video_generation": True,
            "ai_planning": True,
            "script_generation": True,
            "luma_integration": True,
            "feedback_loops": True,
            "analytics": True,
            "task_management": True
        },
        "endpoints": {
            "video_generation": "/generate-video",
            "planning": "/generate-plan",
            "script_generation": "/generate-script",
            "task_execution": "/execute-task",
            "shopify_webhook": "/webhook/shopify",
            "next_gen_hooks": "/next-gen/{ad_id}",
            "analytics": "/analytics/summary",
            "health": "/health",
            "system_info": "/system-info"
        },
        "supported_platforms": ["meta", "tiktok", "shopify"],
        "ai_models": {
            "planning": "gpt-4o",
            "script_generation": "gpt-4o",
            "video_generation": "luma-ai",
            "audio_generation": "elevenlabs/openai-tts"
        }
    }

# =================== MAIN APPLICATION ENTRY POINT ===================

if __name__ == "__main__":
    import uvicorn
    
    # Create outputs directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    
    print("🚀 Starting Relicon Central Highway...")
    print("🎬 Video Generation: Ready")
    print("🧠 AI Planning: Ready")
    print("📊 Feedback Loops: Ready")
    print("⚡ Task Management: Ready")
    print("🌐 Server starting on http://0.0.0.0:8000")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    uvicorn.run(app, host="0.0.0.0", port=3000)