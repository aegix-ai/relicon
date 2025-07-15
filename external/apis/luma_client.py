"""
Luma AI API client for video generation
Handles all interactions with Luma AI video generation service
"""
import requests
import time
import json
from typing import Dict, Any, Optional, List
from config.settings import settings

class LumaClient:
    """Client for Luma AI video generation API"""
    
    def __init__(self):
        self.base_url = "https://api.lumalabs.ai/dream-machine/v1"
        self.headers = settings.get_luma_headers()
        self.timeout = 60
    
    def generate_video(self, prompt: str, duration: int = 5, 
                      aspect_ratio: str = "16:9") -> Optional[str]:
        """
        Generate video using Luma AI
        
        Args:
            prompt: Text prompt for video generation
            duration: Video duration in seconds (5-10)
            aspect_ratio: Video aspect ratio (16:9, 9:16, 1:1)
            
        Returns:
            str: Generation job ID if successful, None otherwise
        """
        try:
            payload = {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "duration": duration,
                "loop": False
            }
            
            response = requests.post(
                f"{self.base_url}/generations",
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 201:
                data = response.json()
                return data.get("id")
            else:
                print(f"Luma API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error generating video with Luma: {e}")
            return None
    
    def check_generation_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check the status of a video generation job
        
        Args:
            job_id: The generation job ID
            
        Returns:
            dict: Status information including state and download URL
        """
        try:
            response = requests.get(
                f"{self.base_url}/generations/{job_id}",
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error checking Luma status: {response.status_code}")
                return {"state": "error", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"Error checking generation status: {e}")
            return {"state": "error", "error": str(e)}
    
    def wait_for_completion(self, job_id: str, max_wait: int = 300, 
                           poll_interval: int = 10) -> Optional[str]:
        """
        Wait for video generation to complete
        
        Args:
            job_id: The generation job ID
            max_wait: Maximum time to wait in seconds
            poll_interval: How often to check status in seconds
            
        Returns:
            str: Download URL if successful, None otherwise
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = self.check_generation_status(job_id)
            state = status.get("state", "unknown")
            
            if state == "completed":
                return status.get("assets", {}).get("video")
            elif state == "failed":
                print(f"Video generation failed: {status.get('failure_reason', 'Unknown error')}")
                return None
            elif state == "error":
                print(f"Error in generation: {status.get('error', 'Unknown error')}")
                return None
            
            # Still processing, wait and check again
            time.sleep(poll_interval)
        
        print(f"Video generation timed out after {max_wait} seconds")
        return None
    
    def download_video(self, video_url: str, output_path: str) -> bool:
        """
        Download generated video from URL
        
        Args:
            video_url: URL to download video from
            output_path: Local path to save video
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.get(video_url, stream=True, timeout=120)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
            else:
                print(f"Error downloading video: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error downloading video: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information and usage limits"""
        try:
            response = requests.get(
                f"{self.base_url}/account",
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def list_generations(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """List recent generations"""
        try:
            params = {"limit": limit, "offset": offset}
            response = requests.get(
                f"{self.base_url}/generations",
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("generations", [])
            else:
                return []
                
        except Exception as e:
            print(f"Error listing generations: {e}")
            return []

# Global Luma client instance
luma_client = LumaClient()