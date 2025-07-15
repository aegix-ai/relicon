"""
API middleware for Relicon AI Video Generation Platform
Handles authentication, logging, and request validation
"""
import hmac
import hashlib
import time
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
from config.settings import settings

class WebhookValidator:
    """Validates webhook signatures from external platforms"""
    
    @staticmethod
    def validate_shopify_webhook(request: Request, payload: bytes) -> bool:
        """Validate Shopify webhook signature"""
        try:
            if not settings.SHOPIFY_WEBHOOK_SECRET:
                return False
            
            signature = request.headers.get("X-Shopify-Hmac-Sha256")
            if not signature:
                return False
            
            expected_signature = hmac.new(
                settings.SHOPIFY_WEBHOOK_SECRET.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            print(f"Error validating Shopify webhook: {e}")
            return False
    
    @staticmethod
    def validate_meta_webhook(request: Request, payload: bytes) -> bool:
        """Validate Meta webhook signature"""
        try:
            # Meta webhook validation would go here
            # For now, return True as we'll implement when needed
            return True
            
        except Exception as e:
            print(f"Error validating Meta webhook: {e}")
            return False
    
    @staticmethod
    def validate_tiktok_webhook(request: Request, payload: bytes) -> bool:
        """Validate TikTok webhook signature"""
        try:
            # TikTok webhook validation would go here
            # For now, return True as we'll implement when needed
            return True
            
        except Exception as e:
            print(f"Error validating TikTok webhook: {e}")
            return False

class RequestLogger:
    """Logs API requests for monitoring and debugging"""
    
    @staticmethod
    def log_request(request: Request, response_time: float, status_code: int):
        """Log API request details"""
        if settings.DEBUG:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
                  f"{request.method} {request.url} - "
                  f"{status_code} - {response_time:.3f}s")
    
    @staticmethod
    def log_error(error: Exception, request: Request):
        """Log error details"""
        print(f"[ERROR] {request.method} {request.url}: {str(error)}")

class RateLimiter:
    """Simple rate limiting for API endpoints"""
    
    def __init__(self):
        self.requests = {}
        self.window_size = 60  # 1 minute window
        self.max_requests = 100  # Max requests per window
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed for client IP"""
        current_time = time.time()
        
        # Clean old entries
        self._cleanup_old_requests(current_time)
        
        # Check current client
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        client_requests = self.requests[client_ip]
        
        # Count requests in current window
        window_start = current_time - self.window_size
        recent_requests = [req_time for req_time in client_requests if req_time > window_start]
        
        if len(recent_requests) >= self.max_requests:
            return False
        
        # Add current request
        recent_requests.append(current_time)
        self.requests[client_ip] = recent_requests
        
        return True
    
    def _cleanup_old_requests(self, current_time: float):
        """Remove old request records"""
        window_start = current_time - self.window_size
        
        for client_ip in list(self.requests.keys()):
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip] 
                if req_time > window_start
            ]
            
            if not self.requests[client_ip]:
                del self.requests[client_ip]

class SecurityHeaders:
    """Adds security headers to responses"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get security headers to add to responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'self'",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        }

# Global instances
webhook_validator = WebhookValidator()
request_logger = RequestLogger()
rate_limiter = RateLimiter()
security_headers = SecurityHeaders()