"""Luma AI client module"""
import os
import requests
from typing import Dict, Any, Optional
from config.settings import settings

class LumaClient:
    """Luma AI client for video generation"""
    
    def __init__(self):
        self.api_key = settings.LUMA_API_KEY
        self.base_url = "https://api.lumalabs.ai"
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        if not self.api_key:
            return {"error": "Luma API key not configured"}
        
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(f"{self.base_url}/account", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def generate_video(self, prompt: str, duration: int = 5) -> Optional[str]:
        """Generate video with Luma AI"""
        if not self.api_key:
            return None
        
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            data = {
                "prompt": prompt,
                "duration": duration
            }
            
            response = requests.post(f"{self.base_url}/generate", headers=headers, json=data)
            
            if response.status_code == 200:
                return response.json().get("job_id")
            
            return None
            
        except Exception as e:
            print(f"Luma API error: {e}")
            return None

# Global instance
luma_client = LumaClient()