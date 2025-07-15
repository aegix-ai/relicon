"""
Creative evaluation system for performance analysis
Analyzes ad performance and identifies winning creatives
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional
from core.database import get_db, Ads, Sales, MetricsMeta, MetricsTT
from ai.agents import hook_generator

class CreativeEvaluator:
    """Evaluates creative performance and identifies winners"""
    
    def __init__(self):
        self.performance_threshold = 0.75  # Top 25% performers
        self.min_spend_threshold = 50.0    # Minimum spend to be considered
        self.min_impressions_threshold = 1000  # Minimum impressions
    
    def evaluate_creatives(self, days: int = 30) -> Dict[str, Any]:
        """
        Evaluate creative performance and identify winners
        
        Args:
            days: Number of days to analyze
            
        Returns:
            dict: Evaluation results with winners and performance metrics
        """
        try:
            with get_db() as db:
                # Get date range
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=days)
                
                # Get all ads with performance data
                ads_performance = self._calculate_ads_performance(db, start_date, end_date)
                
                if not ads_performance:
                    return {"error": "No ads performance data found"}
                
                # Identify winners
                winners = self._identify_winners(ads_performance)
                
                # Update winner tags in database
                self._update_winner_tags(db, winners)
                
                # Calculate summary statistics
                summary = self._calculate_summary(ads_performance, winners)
                
                return {
                    "period": f"{start_date} to {end_date}",
                    "total_ads": len(ads_performance),
                    "winners": len(winners),
                    "summary": summary,
                    "top_performers": winners[:5]  # Top 5 performers
                }
                
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_ads_performance(self, db, start_date: datetime.date, 
                                 end_date: datetime.date) -> List[Dict[str, Any]]:
        """Calculate performance metrics for all ads"""
        ads_performance = []
        
        try:
            # Get all ads
            ads = db.query(Ads).all()
            
            for ad in ads:
                # Get metrics for this ad
                metrics = self._get_ad_metrics(db, ad, start_date, end_date)
                
                if metrics and metrics["spend"] >= self.min_spend_threshold and \
                   metrics["impressions"] >= self.min_impressions_threshold:
                    
                    # Calculate ROAS
                    roas = self._calculate_roas(db, ad, start_date, end_date, metrics["spend"])
                    
                    performance = {
                        "ad_id": ad.ad_id,
                        "platform": ad.platform,
                        "creative_content": ad.creative_content,
                        "impressions": metrics["impressions"],
                        "clicks": metrics["clicks"],
                        "spend": metrics["spend"],
                        "ctr": metrics["ctr"],
                        "cpc": metrics["cpc"],
                        "roas": roas,
                        "performance_score": self._calculate_performance_score(metrics, roas)
                    }
                    
                    ads_performance.append(performance)
            
            return ads_performance
            
        except Exception as e:
            print(f"Error calculating ads performance: {e}")
            return []
    
    def _get_ad_metrics(self, db, ad: Ads, start_date: datetime.date, 
                       end_date: datetime.date) -> Optional[Dict[str, Any]]:
        """Get aggregated metrics for an ad"""
        try:
            if ad.platform == "meta":
                # Get Meta metrics
                metrics = db.query(MetricsMeta).filter(
                    MetricsMeta.ad_id == int(ad.ad_id),
                    MetricsMeta.date >= start_date,
                    MetricsMeta.date <= end_date
                ).all()
            elif ad.platform == "tiktok":
                # Get TikTok metrics
                metrics = db.query(MetricsTT).filter(
                    MetricsTT.ad_id == ad.ad_id,
                    MetricsTT.date >= start_date,
                    MetricsTT.date <= end_date
                ).all()
            else:
                return None
            
            if not metrics:
                return None
            
            # Aggregate metrics
            total_impressions = sum(m.impressions for m in metrics)
            total_clicks = sum(m.clicks for m in metrics)
            total_spend = sum(float(m.spend) for m in metrics)
            
            return {
                "impressions": total_impressions,
                "clicks": total_clicks,
                "spend": total_spend,
                "ctr": (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
                "cpc": (total_spend / total_clicks) if total_clicks > 0 else 0
            }
            
        except Exception as e:
            print(f"Error getting ad metrics: {e}")
            return None
    
    def _calculate_roas(self, db, ad: Ads, start_date: datetime.date, 
                       end_date: datetime.date, spend: float) -> float:
        """Calculate ROAS for an ad"""
        try:
            # Get sales attributed to this ad
            sales = db.query(Sales).filter(
                Sales.ad_code == ad.ad_id,
                Sales.created_at >= datetime.combine(start_date, datetime.min.time()),
                Sales.created_at <= datetime.combine(end_date, datetime.max.time())
            ).all()
            
            total_revenue = sum(float(sale.revenue) for sale in sales)
            
            return (total_revenue / spend) if spend > 0 else 0.0
            
        except Exception as e:
            print(f"Error calculating ROAS: {e}")
            return 0.0
    
    def _calculate_performance_score(self, metrics: Dict[str, Any], roas: float) -> float:
        """Calculate composite performance score"""
        try:
            # Normalize metrics (simple scoring, can be improved)
            ctr_score = min(metrics["ctr"] / 2.0, 1.0)  # Normalize CTR (2% = 1.0)
            roas_score = min(roas / 3.0, 1.0)  # Normalize ROAS (3.0 = 1.0)
            
            # Weight different factors
            score = (ctr_score * 0.3) + (roas_score * 0.7)
            
            return round(score, 3)
            
        except Exception as e:
            print(f"Error calculating performance score: {e}")
            return 0.0
    
    def _identify_winners(self, ads_performance: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify winning ads based on performance"""
        if not ads_performance:
            return []
        
        # Sort by performance score
        sorted_ads = sorted(ads_performance, key=lambda x: x["performance_score"], reverse=True)
        
        # Take top 25%
        winner_count = max(1, int(len(sorted_ads) * self.performance_threshold))
        winners = sorted_ads[:winner_count]
        
        return winners
    
    def _update_winner_tags(self, db, winners: List[Dict[str, Any]]):
        """Update winner tags in database"""
        try:
            # First, clear all existing winner tags
            db.query(Ads).update({"winner_tag": False})
            
            # Set winner tags for identified winners
            for winner in winners:
                ad = db.query(Ads).filter(Ads.ad_id == winner["ad_id"]).first()
                if ad:
                    ad.winner_tag = True
                    ad.roas = Decimal(str(winner["roas"]))
                    ad.updated_at = datetime.utcnow()
            
            db.commit()
            
        except Exception as e:
            print(f"Error updating winner tags: {e}")
            db.rollback()
    
    def _calculate_summary(self, ads_performance: List[Dict[str, Any]], 
                         winners: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics"""
        if not ads_performance:
            return {}
        
        total_spend = sum(ad["spend"] for ad in ads_performance)
        total_impressions = sum(ad["impressions"] for ad in ads_performance)
        total_clicks = sum(ad["clicks"] for ad in ads_performance)
        
        avg_roas = sum(ad["roas"] for ad in ads_performance) / len(ads_performance)
        avg_ctr = sum(ad["ctr"] for ad in ads_performance) / len(ads_performance)
        avg_cpc = sum(ad["cpc"] for ad in ads_performance) / len(ads_performance)
        
        winner_avg_roas = sum(ad["roas"] for ad in winners) / len(winners) if winners else 0
        
        return {
            "total_spend": round(total_spend, 2),
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "avg_roas": round(avg_roas, 2),
            "avg_ctr": round(avg_ctr, 2),
            "avg_cpc": round(avg_cpc, 2),
            "winner_avg_roas": round(winner_avg_roas, 2),
            "performance_improvement": round(
                ((winner_avg_roas - avg_roas) / avg_roas * 100) if avg_roas > 0 else 0, 2
            )
        }
    
    def get_winners_for_hook_generation(self) -> List[Ads]:
        """Get winner ads for hook generation"""
        try:
            with get_db() as db:
                return db.query(Ads).filter(Ads.winner_tag == True).all()
        except Exception as e:
            print(f"Error getting winners: {e}")
            return []
    
    def generate_next_gen_hooks(self, ad_id: str) -> Dict[str, Any]:
        """Generate next-generation hooks for an ad"""
        try:
            with get_db() as db:
                # Get the current ad
                current_ad = db.query(Ads).filter(Ads.ad_id == ad_id).first()
                if not current_ad:
                    return {"error": "Ad not found"}
                
                # Get winner ads
                winner_ads = self.get_winners_for_hook_generation()
                
                # Generate hooks using AI agent
                return hook_generator.generate_next_gen_hooks(winner_ads, current_ad)
                
        except Exception as e:
            return {"error": str(e)}

# Global creative evaluator instance
creative_evaluator = CreativeEvaluator()

# Legacy function for backwards compatibility
def evaluate_creatives(days: int = 30) -> Dict[str, Any]:
    """Legacy function for evaluating creatives"""
    return creative_evaluator.evaluate_creatives(days)