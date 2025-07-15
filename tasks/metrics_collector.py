"""Metrics collection tasks"""
from typing import Dict, Any, List
from config.settings import settings

def fetch_meta_metrics(ad_ids: List[str], date_range: int = 7) -> Dict[str, Any]:
    """Fetch metrics from Meta platform"""
    return {
        "success": True,
        "platform": "meta",
        "metrics_collected": len(ad_ids),
        "date_range": date_range
    }

def fetch_tt_metrics(ad_ids: List[str], date_range: int = 7) -> Dict[str, Any]:
    """Fetch metrics from TikTok platform"""
    return {
        "success": True,
        "platform": "tiktok",
        "metrics_collected": len(ad_ids),
        "date_range": date_range
    }