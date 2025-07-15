"""
Metrics collection system for advertising platforms
Handles data collection from Meta, TikTok, and other advertising platforms
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from core.database import get_db, MetricsMeta, MetricsTT
from config.settings import settings

class MetricsCollector:
    """Collects advertising metrics from various platforms"""
    
    def __init__(self):
        self.meta_token = settings.META_ACCESS_TOKEN
        self.tiktok_token = settings.TIKTOK_ACCESS_TOKEN
    
    def fetch_meta_metrics(self, ad_ids: List[str], 
                          date_range: int = 7) -> Dict[str, Any]:
        """
        Fetch metrics from Meta/Facebook Ads API
        
        Args:
            ad_ids: List of ad IDs to fetch metrics for
            date_range: Number of days to look back
            
        Returns:
            dict: Results summary with success/failure counts
        """
        if not self.meta_token:
            return {"error": "Meta access token not configured"}
        
        results = {"success": 0, "failed": 0, "errors": []}
        
        try:
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=date_range)
            
            with get_db() as db:
                for ad_id in ad_ids:
                    try:
                        # Fetch metrics from Meta API
                        metrics = self._fetch_meta_ad_metrics(ad_id, start_date, end_date)
                        
                        if metrics:
                            # Store in database
                            self._store_meta_metrics(db, ad_id, metrics)
                            results["success"] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"No metrics found for ad {ad_id}")
                            
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(f"Error fetching ad {ad_id}: {str(e)}")
                
                db.commit()
                
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    def _fetch_meta_ad_metrics(self, ad_id: str, start_date: datetime.date, 
                              end_date: datetime.date) -> Optional[Dict[str, Any]]:
        """Fetch metrics for a single Meta ad"""
        try:
            url = f"https://graph.facebook.com/v18.0/{ad_id}/insights"
            
            params = {
                "access_token": self.meta_token,
                "time_range": json.dumps({
                    "since": start_date.isoformat(),
                    "until": end_date.isoformat()
                }),
                "fields": "impressions,clicks,spend",
                "time_increment": "1"
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                print(f"Meta API error for ad {ad_id}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching Meta metrics for ad {ad_id}: {e}")
            return None
    
    def _store_meta_metrics(self, db, ad_id: str, metrics_data: List[Dict[str, Any]]):
        """Store Meta metrics in database"""
        for metric in metrics_data:
            try:
                # Parse the date
                date_str = metric.get("date_start")
                if not date_str:
                    continue
                
                metric_date = datetime.fromisoformat(date_str).date()
                
                # Check if record already exists
                existing = db.query(MetricsMeta).filter(
                    MetricsMeta.ad_id == int(ad_id),
                    MetricsMeta.date == metric_date
                ).first()
                
                if existing:
                    # Update existing record
                    existing.impressions = int(metric.get("impressions", 0))
                    existing.clicks = int(metric.get("clicks", 0))
                    existing.spend = float(metric.get("spend", 0.0))
                else:
                    # Create new record
                    new_metric = MetricsMeta(
                        ad_id=int(ad_id),
                        date=metric_date,
                        impressions=int(metric.get("impressions", 0)),
                        clicks=int(metric.get("clicks", 0)),
                        spend=float(metric.get("spend", 0.0))
                    )
                    db.add(new_metric)
                    
            except Exception as e:
                print(f"Error storing Meta metric: {e}")
    
    def fetch_tiktok_metrics(self, ad_ids: List[str], 
                           date_range: int = 7) -> Dict[str, Any]:
        """
        Fetch metrics from TikTok Ads API
        
        Args:
            ad_ids: List of ad IDs to fetch metrics for
            date_range: Number of days to look back
            
        Returns:
            dict: Results summary with success/failure counts
        """
        if not self.tiktok_token:
            return {"error": "TikTok access token not configured"}
        
        results = {"success": 0, "failed": 0, "errors": []}
        
        try:
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=date_range)
            
            with get_db() as db:
                for ad_id in ad_ids:
                    try:
                        # Fetch metrics from TikTok API
                        metrics = self._fetch_tiktok_ad_metrics(ad_id, start_date, end_date)
                        
                        if metrics:
                            # Store in database
                            self._store_tiktok_metrics(db, ad_id, metrics)
                            results["success"] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"No metrics found for ad {ad_id}")
                            
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(f"Error fetching ad {ad_id}: {str(e)}")
                
                db.commit()
                
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    def _fetch_tiktok_ad_metrics(self, ad_id: str, start_date: datetime.date, 
                               end_date: datetime.date) -> Optional[List[Dict[str, Any]]]:
        """Fetch metrics for a single TikTok ad"""
        try:
            url = "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/"
            
            headers = {
                "Access-Token": self.tiktok_token,
                "Content-Type": "application/json"
            }
            
            data = {
                "service_type": "AUCTION",
                "report_type": "BASIC",
                "data_level": "AUCTION_AD",
                "dimensions": ["ad_id", "stat_time_day"],
                "metrics": ["impressions", "clicks", "spend"],
                "filters": [
                    {
                        "field_name": "ad_ids",
                        "filter_type": "IN",
                        "filter_value": [ad_id]
                    }
                ],
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "page": 1,
                "page_size": 1000
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    return result.get("data", {}).get("list", [])
                else:
                    print(f"TikTok API error for ad {ad_id}: {result.get('message')}")
                    return None
            else:
                print(f"TikTok API HTTP error for ad {ad_id}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching TikTok metrics for ad {ad_id}: {e}")
            return None
    
    def _store_tiktok_metrics(self, db, ad_id: str, metrics_data: List[Dict[str, Any]]):
        """Store TikTok metrics in database"""
        for metric in metrics_data:
            try:
                # Parse the date
                date_str = metric.get("dimensions", {}).get("stat_time_day")
                if not date_str:
                    continue
                
                metric_date = datetime.fromisoformat(date_str).date()
                
                # Check if record already exists
                existing = db.query(MetricsTT).filter(
                    MetricsTT.ad_id == ad_id,
                    MetricsTT.date == metric_date
                ).first()
                
                metrics_values = metric.get("metrics", {})
                
                if existing:
                    # Update existing record
                    existing.impressions = int(metrics_values.get("impressions", 0))
                    existing.clicks = int(metrics_values.get("clicks", 0))
                    existing.spend = float(metrics_values.get("spend", 0.0))
                else:
                    # Create new record
                    new_metric = MetricsTT(
                        ad_id=ad_id,
                        date=metric_date,
                        impressions=int(metrics_values.get("impressions", 0)),
                        clicks=int(metrics_values.get("clicks", 0)),
                        spend=float(metrics_values.get("spend", 0.0))
                    )
                    db.add(new_metric)
                    
            except Exception as e:
                print(f"Error storing TikTok metric: {e}")
    
    def get_metrics_summary(self, platform: str = "all", 
                          days: int = 30) -> Dict[str, Any]:
        """Get metrics summary for specified platform and time period"""
        try:
            with get_db() as db:
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=days)
                
                summary = {
                    "period": f"{start_date} to {end_date}",
                    "platforms": {}
                }
                
                if platform in ["all", "meta"]:
                    meta_metrics = db.query(MetricsMeta).filter(
                        MetricsMeta.date >= start_date,
                        MetricsMeta.date <= end_date
                    ).all()
                    
                    summary["platforms"]["meta"] = self._calculate_platform_summary(meta_metrics)
                
                if platform in ["all", "tiktok"]:
                    tiktok_metrics = db.query(MetricsTT).filter(
                        MetricsTT.date >= start_date,
                        MetricsTT.date <= end_date
                    ).all()
                    
                    summary["platforms"]["tiktok"] = self._calculate_platform_summary(tiktok_metrics)
                
                return summary
                
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_platform_summary(self, metrics: List) -> Dict[str, Any]:
        """Calculate summary statistics for platform metrics"""
        if not metrics:
            return {"impressions": 0, "clicks": 0, "spend": 0.0, "ads": 0}
        
        total_impressions = sum(m.impressions for m in metrics)
        total_clicks = sum(m.clicks for m in metrics)
        total_spend = sum(float(m.spend) for m in metrics)
        unique_ads = len(set(m.ad_id for m in metrics))
        
        return {
            "impressions": total_impressions,
            "clicks": total_clicks,
            "spend": round(total_spend, 2),
            "ads": unique_ads,
            "ctr": round((total_clicks / total_impressions * 100) if total_impressions > 0 else 0, 2),
            "cpc": round((total_spend / total_clicks) if total_clicks > 0 else 0, 2)
        }

# Global metrics collector instance
metrics_collector = MetricsCollector()

# Legacy functions for backwards compatibility
def fetch_meta_metrics(ad_ids: List[str], date_range: int = 7) -> Dict[str, Any]:
    """Legacy function for fetching Meta metrics"""
    return metrics_collector.fetch_meta_metrics(ad_ids, date_range)

def fetch_tt_metrics(ad_ids: List[str], date_range: int = 7) -> Dict[str, Any]:
    """Legacy function for fetching TikTok metrics"""
    return metrics_collector.fetch_tiktok_metrics(ad_ids, date_range)