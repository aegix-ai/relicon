"""
Main FastAPI application for Relicon - The Central Highway
Unified entry point for all video generation, AI planning, feedback loops, and task management
"""
import os
import json
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Core system imports
from config.settings import settings
from core.database import get_db, init_db, Sales, Ads
from core.api import (
    ShopifyWebhookData, MetaPlatformData, TikTokWebhookData,
    VideoGenerationRequest, VideoGenerationResponse,
    MetricsRequest, MetricsResponse,
    HookGenerationRequest, HookGenerationResponse,
    EvaluationRequest, EvaluationResponse,
    ErrorResponse, webhook_validator
)

# AI and video generation services
from ai.agents import generate_next_gen_hooks
from video.services import video_service
from tasks import fetch_meta_metrics, fetch_tt_metrics, evaluate_creatives

# Initialize FastAPI app - Central Highway
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/outputs", StaticFiles(directory=settings.OUTPUT_DIR), name="outputs")

# Initialize database and services on startup
@app.on_event("startup")
async def startup_event():
    """Initialize all services on startup"""
    init_db()
    print("✓ Database initialized successfully!")
    print("✓ Video generation services initialized!")
    print("✓ AI planning services initialized!")
    print("✓ Task management services initialized!")
    print("🚀 Relicon Central Highway is ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Relicon Central Highway shutting down...")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION
    }

# Video generation endpoints
@app.post("/api/generate-video", response_model=VideoGenerationResponse)
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate AI video advertisement"""
    try:
        # Convert request to brand info
        brand_info = {
            "brand_name": request.brand_name,
            "brand_description": request.brand_description,
            "duration": request.duration,
            "platform": request.platform,
            "target_audience": request.target_audience,
            "style": request.style
        }
        
        # Generate video
        result = video_service.generate_video(brand_info)
        
        if result.get("success"):
            return VideoGenerationResponse(
                success=True,
                message="Video generated successfully",
                video_url=result.get("video_url"),
                job_id=f"job_{int(time.time())}"
            )
        else:
            return VideoGenerationResponse(
                success=False,
                message="Video generation failed",
                error=result.get("error", "Unknown error")
            )
            
    except Exception as e:
        return VideoGenerationResponse(
            success=False,
            message="Internal server error",
            error=str(e)
        )

@app.post("/api/generate-simple-video", response_model=VideoGenerationResponse)
async def generate_simple_video(
    request: VideoGenerationRequest,
    db: Session = Depends(get_db)
):
    """Generate simple video without Luma AI (faster)"""
    try:
        brand_info = {
            "brand_name": request.brand_name,
            "brand_description": request.brand_description,
            "duration": request.duration,
            "platform": request.platform
        }
        
        result = video_service.create_simple_video(brand_info)
        
        if result.get("success"):
            return VideoGenerationResponse(
                success=True,
                message="Simple video generated successfully",
                video_url=result.get("video_url"),
                job_id=f"simple_{int(time.time())}"
            )
        else:
            return VideoGenerationResponse(
                success=False,
                message="Simple video generation failed",
                error=result.get("error", "Unknown error")
            )
            
    except Exception as e:
        return VideoGenerationResponse(
            success=False,
            message="Internal server error",
            error=str(e)
        )

# Hook generation endpoints
@app.post("/api/generate-hooks", response_model=HookGenerationResponse)
async def generate_hooks(
    request: HookGenerationRequest,
    db: Session = Depends(get_db)
):
    """Generate next-generation hooks based on winning ads"""
    try:
        # Get current ad
        current_ad = db.query(Ads).filter(Ads.ad_id == request.ad_id).first()
        if not current_ad:
            return HookGenerationResponse(
                success=False,
                error="Ad not found"
            )
        
        # Get winner ads
        winner_ads = db.query(Ads).filter(Ads.winner_tag == True).all()
        
        # Generate hooks
        result = generate_next_gen_hooks(winner_ads, current_ad)
        
        return HookGenerationResponse(
            success=True,
            hooks=result.get("hooks", []),
            analysis_summary=result.get("analysis_summary"),
            winning_patterns=result.get("winning_patterns", [])
        )
        
    except Exception as e:
        return HookGenerationResponse(
            success=False,
            error=str(e)
        )

# Metrics collection endpoints
@app.post("/api/collect-metrics", response_model=MetricsResponse)
async def collect_metrics(
    request: MetricsRequest,
    background_tasks: BackgroundTasks
):
    """Collect metrics from advertising platforms"""
    try:
        if request.platform == "meta":
            result = fetch_meta_metrics(request.ad_ids, request.date_range)
        elif request.platform == "tiktok":
            result = fetch_tt_metrics(request.ad_ids, request.date_range)
        else:
            return MetricsResponse(
                success=False,
                platform=request.platform,
                processed=0,
                failed=0,
                errors=["Unsupported platform"]
            )
        
        return MetricsResponse(
            success=not result.get("error"),
            platform=request.platform,
            processed=result.get("success", 0),
            failed=result.get("failed", 0),
            errors=result.get("errors", [])
        )
        
    except Exception as e:
        return MetricsResponse(
            success=False,
            platform=request.platform,
            processed=0,
            failed=0,
            errors=[str(e)]
        )

# Creative evaluation endpoints
@app.post("/api/evaluate-creatives", response_model=EvaluationResponse)
async def evaluate_creatives_endpoint(
    request: EvaluationRequest,
    db: Session = Depends(get_db)
):
    """Evaluate creative performance and identify winners"""
    try:
        result = evaluate_creatives(request.days)
        
        if result.get("error"):
            return EvaluationResponse(
                success=False,
                error=result["error"],
                period="",
                total_ads=0,
                winners=0
            )
        
        return EvaluationResponse(
            success=True,
            period=result.get("period", ""),
            total_ads=result.get("total_ads", 0),
            winners=result.get("winners", 0),
            summary=result.get("summary", {}),
            top_performers=result.get("top_performers", [])
        )
        
    except Exception as e:
        return EvaluationResponse(
            success=False,
            error=str(e),
            period="",
            total_ads=0,
            winners=0
        )

# Webhook endpoints
@app.post("/webhooks/shopify")
async def shopify_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Shopify webhook for sales tracking"""
    try:
        body = await request.body()
        
        # Validate webhook signature
        if not webhook_validator.validate_shopify_webhook(request, body):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Parse webhook data
        data = json.loads(body)
        webhook_data = ShopifyWebhookData(**data)
        
        # Extract UTM content (ad code)
        ad_code = None
        for attr in webhook_data.note_attributes:
            if attr.get("name") == "utm_content":
                ad_code = attr.get("value")
                break
        
        # Store sales data
        sale = Sales(
            order_id=webhook_data.id,
            ad_code=ad_code,
            revenue=float(webhook_data.total_price)
        )
        db.add(sale)
        db.commit()
        
        return {"status": "success", "message": "Sale recorded"}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/webhooks/meta")
async def meta_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Meta platform webhook"""
    try:
        body = await request.body()
        
        # Validate webhook signature
        if not webhook_validator.validate_meta_webhook(request, body):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Process Meta webhook data
        data = json.loads(body)
        # Meta webhook processing logic would go here
        
        return {"status": "success", "message": "Meta webhook processed"}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/webhooks/tiktok")
async def tiktok_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle TikTok webhook"""
    try:
        body = await request.body()
        
        # Validate webhook signature
        if not webhook_validator.validate_tiktok_webhook(request, body):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Process TikTok webhook data
        data = json.loads(body)
        # TikTok webhook processing logic would go here
        
        return {"status": "success", "message": "TikTok webhook processed"}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# File upload endpoint
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload file endpoint"""
    try:
        # Save uploaded file
        upload_dir = Path(settings.ASSETS_DIR) / "uploads"
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "success": True,
            "filename": file.filename,
            "path": str(file_path)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Development endpoints
@app.get("/api/test-video")
async def test_video():
    """Test video generation with sample data"""
    try:
        brand_info = {
            "brand_name": "Test Brand",
            "brand_description": "Amazing product for testing",
            "duration": 15,
            "platform": "universal"
        }
        
        result = video_service.create_simple_video(brand_info)
        return result
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    try:
        ads_count = db.query(Ads).count()
        sales_count = db.query(Sales).count()
        winners_count = db.query(Ads).filter(Ads.winner_tag == True).count()
        
        return {
            "ads": ads_count,
            "sales": sales_count,
            "winners": winners_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {"error": str(e)}

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)