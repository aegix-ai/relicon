"""
Pydantic schemas for API request/response models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class GenerateRequest(BaseModel):
    brand_name: str = Field(..., description="Name of the brand/product")
    brand_description: str = Field(..., description="Detailed description of the brand/product")
    target_audience: Optional[str] = Field(None, description="Target audience demographic")
    tone: Optional[str] = Field("professional", description="Tone of the ad (professional, casual, energetic, etc.)")
    duration: Optional[int] = Field(30, ge=15, le=60, description="Desired video duration in seconds")
    call_to_action: Optional[str] = Field(None, description="Specific call-to-action text")
    brand_assets: Optional[List[str]] = Field(default_factory=list, description="List of uploaded asset IDs")
    custom_requirements: Optional[str] = Field(None, description="Any custom requirements or preferences")


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str


class JobStatus(BaseModel):
    job_id: str
    status: str  # queued, processing, completed, failed
    progress: int = Field(ge=0, le=100, description="Progress percentage")
    message: str
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    video_url: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ConceptResult(BaseModel):
    concept: str
    hook: str
    tone: str
    key_points: List[str]
    visual_style: str
    estimated_duration: int


class ScriptSegment(BaseModel):
    scene: int
    voiceover: str
    visual_hint: str
    duration: Optional[float] = None


class TimelineItem(BaseModel):
    type: str  # "video", "audio", "transition", "effect"
    path: Optional[str] = None
    duration: float
    start_time: float = 0
    properties: Optional[Dict[str, Any]] = None


class FFmpegCommand(BaseModel):
    inputs: List[str]
    filter_complex: str
    output_path: str
    estimated_duration: int
