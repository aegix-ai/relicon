"""Celery tasks for Relicon feedback loop."""
import os
import json
import requests
from datetime import datetime, date
from typing import List
from celery import Celery
from celery.schedules import crontab
from sqlalchemy.orm import Session
from sqlalchemy import text
# Configuration using environment variables

from database import SessionLocal, MetricsMeta, MetricsTT, Sales, Ads

# Initialize Celery app
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app = Celery("relicon_tasks", broker=redis_url, backend=redis_url)

# Celery configuration
app.conf.timezone = "UTC"
app.conf.beat_schedule = {
    "fetch-meta-metrics": {
        "task": "tasks.fetch_meta_metrics",
        "schedule": crontab(hour=2, minute=0),  # 02:00 UTC daily
        "args": ([],),  # Will fetch all active ad_ids
    },
    "fetch-tt-metrics": {
        "task": "tasks.fetch_tt_metrics", 
        "schedule": crontab(hour=2, minute=15),  # 02:15 UTC daily
        "args": ([],),  # Will fetch all active ad_ids
    },
    "evaluate-creatives": {
        "task": "tasks.evaluate_creatives",
        "schedule": crontab(hour=3, minute=0),  # 03:00 UTC daily
    },
}


@app.task(bind=True, retry_backoff=True, max_retries=3)
def fetch_meta_metrics(self, ad_ids: List[int] = None):
    """Fetch Facebook/Meta ad metrics and store in database."""
    try:
        db = SessionLocal()
        access_token = os.getenv("META_ACCESS_TOKEN")
        
        if not ad_ids:
            # Get all active Meta ad IDs from database
            ad_ids = db.query(Ads.ad_id).filter(Ads.platform == "meta").all()
            ad_ids = [int(ad[0]) for ad in ad_ids]
        
        if not ad_ids:
            print("No Meta ad IDs found")
            return {"status": "success", "message": "No ad IDs to process"}
        
        today = date.today()
        results = []
        
        for ad_id in ad_ids:
            try:
                # Fetch metrics from Facebook Graph API
                url = f"https://graph.facebook.com/v19.0/{ad_id}/insights"
                params = {
                    "fields": "impressions,clicks,spend,actions",
                    "access_token": access_token,
                    "date_preset": "yesterday"
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data.get("data"):
                    continue
                
                insight = data["data"][0]
                
                # Upsert metrics
                existing = db.query(MetricsMeta).filter(
                    MetricsMeta.ad_id == ad_id,
                    MetricsMeta.date == today
                ).first()
                
                if existing:
                    existing.impressions = int(insight.get("impressions", 0))
                    existing.clicks = int(insight.get("clicks", 0))
                    existing.spend = float(insight.get("spend", 0))
                else:
                    metric = MetricsMeta(
                        ad_id=ad_id,
                        date=today,
                        impressions=int(insight.get("impressions", 0)),
                        clicks=int(insight.get("clicks", 0)),
                        spend=float(insight.get("spend", 0))
                    )
                    db.add(metric)
                
                results.append(f"Updated ad_id {ad_id}")
                
            except requests.RequestException as e:
                print(f"Error fetching data for ad {ad_id}: {e}")
                continue
        
        db.commit()
        return {"status": "success", "updated": len(results), "results": results}
        
    except Exception as e:
        print(f"Error in fetch_meta_metrics: {e}")
        db.rollback()
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()


@app.task(bind=True, retry_backoff=True, max_retries=3)
def fetch_tt_metrics(self, ad_ids: List[str] = None):
    """Fetch TikTok ad metrics and store in database."""
    try:
        db = SessionLocal()
        access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        
        if not ad_ids:
            # Get all active TikTok ad IDs from database
            ad_ids = db.query(Ads.ad_id).filter(Ads.platform == "tiktok").all()
            ad_ids = [ad[0] for ad in ad_ids]
        
        if not ad_ids:
            print("No TikTok ad IDs found")
            return {"status": "success", "message": "No ad IDs to process"}
        
        today = date.today()
        results = []
        
        # TikTok API request payload
        payload = {
            "report_type": "BASIC",
            "data_level": "AUCTION_AD",
            "dimensions": ["ad_id"],
            "metrics": ["impressions", "clicks", "spend"],
            "start_date": today.strftime("%Y-%m-%d"),
            "end_date": today.strftime("%Y-%m-%d"),
            "filters": {
                "ad_ids": ad_ids
            }
        }
        
        headers = {
            "Access-Token": access_token,
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://business-api.tiktok.com/open_api/v2.0/report/integrated/get/",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0 and data.get("data", {}).get("list"):
            for item in data["data"]["list"]:
                ad_id = item.get("dimensions", {}).get("ad_id")
                metrics = item.get("metrics", {})
                
                if not ad_id:
                    continue
                
                # Upsert metrics
                existing = db.query(MetricsTT).filter(
                    MetricsTT.ad_id == ad_id,
                    MetricsTT.date == today
                ).first()
                
                if existing:
                    existing.impressions = int(metrics.get("impressions", 0))
                    existing.clicks = int(metrics.get("clicks", 0))
                    existing.spend = float(metrics.get("spend", 0))
                else:
                    metric = MetricsTT(
                        ad_id=ad_id,
                        date=today,
                        impressions=int(metrics.get("impressions", 0)),
                        clicks=int(metrics.get("clicks", 0)),
                        spend=float(metrics.get("spend", 0))
                    )
                    db.add(metric)
                
                results.append(f"Updated ad_id {ad_id}")
        
        db.commit()
        return {"status": "success", "updated": len(results), "results": results}
        
    except Exception as e:
        print(f"Error in fetch_tt_metrics: {e}")
        db.rollback()
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()


@app.task(bind=True)
def evaluate_creatives(self):
    """Evaluate creative performance and mark winners."""
    try:
        db = SessionLocal()
        
        # Complex SQL query to calculate ROAS
        sql = text("""
            WITH combined_metrics AS (
                SELECT 
                    a.ad_id,
                    a.platform,
                    COALESCE(SUM(mm.spend), 0) + COALESCE(SUM(mt.spend), 0) as total_spend,
                    COUNT(DISTINCT CASE WHEN mm.ad_id IS NOT NULL THEN mm.date END) as meta_days,
                    COUNT(DISTINCT CASE WHEN mt.ad_id IS NOT NULL THEN mt.date END) as tt_days
                FROM ads a
                LEFT JOIN metrics_meta mm ON CAST(a.ad_id AS TEXT) = CAST(mm.ad_id AS TEXT) AND a.platform = 'meta'
                LEFT JOIN metrics_tt mt ON a.ad_id = mt.ad_id AND a.platform = 'tiktok'
                WHERE a.created_at >= NOW() - INTERVAL '30 days'
                GROUP BY a.ad_id, a.platform
            ),
            revenue_by_ad AS (
                SELECT 
                    s.ad_code,
                    SUM(s.revenue) as total_revenue
                FROM sales s
                WHERE s.created_at >= NOW() - INTERVAL '30 days'
                AND s.ad_code IS NOT NULL
                GROUP BY s.ad_code
            ),
            ad_performance AS (
                SELECT 
                    cm.ad_id,
                    cm.platform,
                    cm.total_spend,
                    COALESCE(rba.total_revenue, 0) as total_revenue,
                    CASE 
                        WHEN cm.total_spend > 0 THEN COALESCE(rba.total_revenue, 0) / cm.total_spend
                        ELSE 0
                    END as roas
                FROM combined_metrics cm
                LEFT JOIN revenue_by_ad rba ON cm.ad_id = rba.ad_code
            )
            SELECT 
                ad_id,
                platform,
                total_spend,
                total_revenue,
                roas,
                CASE 
                    WHEN roas >= (SELECT PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY roas) FROM ad_performance WHERE roas > 0)
                    THEN true
                    ELSE false
                END as is_winner
            FROM ad_performance
            ORDER BY roas DESC
        """)
        
        results = db.execute(sql).fetchall()
        
        # Reset all winner tags first
        db.query(Ads).update({Ads.winner_tag: False})
        
        # Update ads with new performance data
        updated_count = 0
        for row in results:
            ad = db.query(Ads).filter(Ads.ad_id == row.ad_id).first()
            if ad:
                ad.roas = float(row.roas)
                ad.winner_tag = bool(row.is_winner)
                updated_count += 1
        
        db.commit()
        
        winners = db.query(Ads).filter(Ads.winner_tag == True).count()
        
        return {
            "status": "success",
            "updated_ads": updated_count,
            "winners_identified": winners,
            "message": f"Evaluated {updated_count} ads, identified {winners} winners"
        }
        
    except Exception as e:
        print(f"Error in evaluate_creatives: {e}")
        db.rollback()
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()


if __name__ == "__main__":
    app.start()