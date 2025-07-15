"""
API models and schemas for Relicon AI Video Generation Platform
Defines all request/response models for the FastAPI application
"""
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class ShopifyWebhookData(BaseModel):
    """Shopify webhook data model"""
    id: int
    total_price: str
    customer: Dict[str, Any] = {}
    line_items: List[Dict[str, Any]] = []
    note_attributes: List[Dict[str, Any]] = []

class MetaPlatformData(BaseModel):
    """Meta platform webhook data model"""
    object: str
    entry: List[Dict[str, Any]]

class TikTokWebhookData(BaseModel):
    """TikTok webhook data model"""
    event: str
    data: Dict[str, Any]

class VideoGenerationRequest(BaseModel):
    """Video generation request model"""
    brand_name: str
    brand_description: str
    duration: int = 30
    platform: str = "universal"
    target_audience: Optional[str] = None
    style: Optional[str] = None

class VideoGenerationResponse(BaseModel):
    """Video generation response model"""
    success: bool
    message: str
    video_url: Optional[str] = None
    job_id: Optional[str] = None
    error: Optional[str] = None

class MetricsRequest(BaseModel):
    """Metrics collection request model"""
    platform: str
    ad_ids: List[str]
    date_range: int = 7

class MetricsResponse(BaseModel):
    """Metrics collection response model"""
    success: bool
    platform: str
    processed: int
    failed: int
    errors: List[str] = []

class HookGenerationRequest(BaseModel):
    """Hook generation request model"""
    ad_id: str
    platform: Optional[str] = None
    target_audience: Optional[str] = None

class HookGenerationResponse(BaseModel):
    """Hook generation response model"""
    success: bool
    hooks: List[Dict[str, Any]] = []
    analysis_summary: Optional[str] = None
    winning_patterns: List[str] = []
    error: Optional[str] = None

class EvaluationRequest(BaseModel):
    """Creative evaluation request model"""
    days: int = 30
    platform: Optional[str] = None

class EvaluationResponse(BaseModel):
    """Creative evaluation response model"""
    success: bool
    period: str
    total_ads: int
    winners: int
    summary: Dict[str, Any] = {}
    top_performers: List[Dict[str, Any]] = []
    error: Optional[str] = None

class ProgressUpdate(BaseModel):
    """Progress update model for real-time updates"""
    progress: int
    message: str
    timestamp: Optional[str] = None

class ErrorResponse(BaseModel):
    """Standard error response model"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None