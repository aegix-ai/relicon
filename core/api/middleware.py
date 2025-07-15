"""API middleware for authentication and validation"""
import hmac
import hashlib
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
from config.settings import settings

class WebhookValidator:
    """Validates webhook signatures"""
    
    def validate_shopify_webhook(self, request: Request, payload: bytes) -> bool:
        """Validate Shopify webhook signature"""
        if not settings.SHOPIFY_WEBHOOK_SECRET:
            return False
        
        signature = request.headers.get('X-Shopify-Hmac-Sha256')
        if not signature:
            return False
        
        expected_signature = hmac.new(
            settings.SHOPIFY_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def validate_meta_webhook(self, request: Request, payload: bytes) -> bool:
        """Validate Meta webhook signature"""
        # Meta webhook validation logic would go here
        return True  # Placeholder
    
    def validate_tiktok_webhook(self, request: Request, payload: bytes) -> bool:
        """Validate TikTok webhook signature"""
        # TikTok webhook validation logic would go here
        return True  # Placeholder

# Global webhook validator
webhook_validator = WebhookValidator()