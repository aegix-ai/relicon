"""API models for request/response validation"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class VideoGenerationRequest(BaseModel):
    """Request model for video generation"""
    brand_name: str = Field(..., description="Brand name")
    brand_description: str = Field(..., description="Brand description")
    duration: int = Field(30, ge=5, le=120, description="Video duration in seconds")
    platform: str = Field("universal", description="Target platform")
    target_audience: Optional[str] = Field(None, description="Target audience")
    style: Optional[str] = Field(None, description="Video style")

class VideoGenerationResponse(BaseModel):
    """Response model for video generation"""
    success: bool
    message: str
    video_url: Optional[str] = None
    job_id: Optional[str] = None
    error: Optional[str] = None

class HookGenerationRequest(BaseModel):
    """Request model for hook generation"""
    winner_ads: List[Dict[str, Any]]
    current_ad: Dict[str, Any]

class HookGenerationResponse(BaseModel):
    """Response model for hook generation"""
    success: bool
    hooks: List[Dict[str, Any]]
    analysis_summary: Optional[str] = None
    error: Optional[str] = None

class MetricsRequest(BaseModel):
    """Request model for metrics collection"""
    platform: str = Field(..., description="Platform (meta, tiktok)")
    ad_ids: List[str] = Field(..., description="Ad IDs to collect metrics for")
    date_range: int = Field(7, description="Date range in days")

class MetricsResponse(BaseModel):
    """Response model for metrics collection"""
    success: bool
    platform: str
    metrics_collected: int
    error: Optional[str] = None

class EvaluationRequest(BaseModel):
    """Request model for creative evaluation"""
    days: int = Field(30, description="Days to evaluate")
    platform: Optional[str] = Field(None, description="Platform filter")

class EvaluationResponse(BaseModel):
    """Response model for creative evaluation"""
    success: bool
    total_ads: int
    winners: int
    performance_summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    message: str
    status_code: int

class ShopifyWebhookData(BaseModel):
    """Shopify webhook data"""
    order_id: str
    total_price: float
    line_items: List[Dict[str, Any]]
    customer: Dict[str, Any]

class MetaPlatformData(BaseModel):
    """Meta platform webhook data"""
    ad_id: str
    campaign_id: str
    metrics: Dict[str, Any]

class TikTokWebhookData(BaseModel):
    """TikTok webhook data"""
    ad_id: str
    campaign_id: str
    metrics: Dict[str, Any]