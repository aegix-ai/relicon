"""Main FastAPI application for Relicon feedback loop."""
import os
import hmac
import hashlib
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
# Configuration using environment variables

from database import get_db, init_db, Sales, Ads
from agent import generate_next_gen_hooks

# Initialize FastAPI app
app = FastAPI(title="Relicon Feedback Loop API", version="1.0.0")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("Database initialized successfully!")


class ShopifyWebhookData(BaseModel):
    """Shopify webhook data model."""
    id: int
    total_price: str
    customer: Dict[str, Any] = {}
    line_items: list = []
    note_attributes: list = []
    landing_site: str = ""
    referring_site: str = ""


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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)