"""
  Luma AI video generation provider implementation.
"""

import os
import requests
import time
from typing import Dict, Any, Optional
from interfaces.video_generator import VideoGenerator


class LumaProvider(VideoGenerator):
    """Luma AI video generation service implementation."""
    
    def __init__(self):
        self.api_key = os.environ.get("LUMA_API_KEY")
        if not self.api_key:
            raise ValueError("LUMA_API_KEY environment variable is required")
        
        self.base_url = "https://api.lumalabs.ai/dream-machine/v1/generations"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_video(self, prompt: str, aspect_ratio: str = "9:16", 
                      image_url: Optional[str] = None, force_unique: bool = False, **kwargs) -> str:
        """Generate video using Luma AI with enhanced prompts."""
        
        # Enhance prompt for cinematic quality if force_unique is True
        if force_unique:
            # Modern commercial elements for Luma
            cinematic_elements = [
                "professional commercial cinematography with dynamic product showcase",
                "cinematic depth of field emphasizing product features and benefits",
                "golden hour lighting creating premium product aesthetics",
                "commercial-grade color grading highlighting brand identity",
                "sleek modern commercial visual style with product focus",
                "high-end product photography with lifestyle integration"
            ]
            
            # Product demonstration and lifestyle elements
            technical_elements = [
                "dynamic product demonstration with clear benefit visualization",
                "smooth camera movements following product usage and workflow",
                "macro details highlighting product quality and craftsmanship",
                "lifestyle integration showing product in natural environments",
                "before-and-after transformation sequences demonstrating results",
                "premium commercial production values with modern aesthetics"
            ]
            
            import random
            selected_cinematic = random.choice(cinematic_elements)
            selected_technical = random.choice(technical_elements)
            
            enhanced_prompt = f"{prompt}, {selected_cinematic}, {selected_technical}"
        else:
            enhanced_prompt = prompt
            
        payload = {
            "prompt": enhanced_prompt,
            "aspect_ratio": aspect_ratio,
            "model": "ray-2",  # Ray-2 is the latest model available via API (Ray-3 not yet in API)
            "resolution": "720p",  # Cost-optimized resolution: 720p = $0.4 vs 1080p = $0.9 per 5s
            "duration": "5s"  # Optimal duration for 3-scene structure (compatible with both Luma and Hailuo)
        }
        
        # Add realism validation for all prompts
        realism_suffix = ", realistic technology with complete components, no floating parts, physically accurate interactions"
        enhanced_prompt_with_realism = f"{enhanced_prompt}{realism_suffix}"
        
        if image_url:
            # Enhanced Luma keyframes structure for better product integration
            payload["keyframes"] = {"frame0": {"type": "image", "url": image_url}}
            
            # Override prompt for better product showcase when using image
            product_prompt = f"Transform this product image into dynamic commercial video, {enhanced_prompt_with_realism}, maintaining product visibility and focus throughout, smooth camera movement showcasing product details, professional product demonstration"
            payload["prompt"] = product_prompt
            
            print(f"Using product image keyframe with enhanced prompt for better integration")
        else:
            # Use enhanced prompt with realism validation
            payload["prompt"] = enhanced_prompt_with_realism
        
        print(f"Starting Luma generation with prompt: {payload['prompt'][:100]}...")
        print(f"Luma payload: {payload}")
        
        response = requests.post(self.base_url, json=payload, headers=self.headers)
        
        if response.status_code != 201:
            raise Exception(f"Failed to create Luma generation: {response.status_code} - {response.text}")
        
        generation_data = response.json()
        generation_id = generation_data.get("id")
        
        if not generation_id:
            raise Exception("Could not extract generation ID from Luma response")
        
        print(f"Luma generation started with ID: {generation_id}")
        
        # Poll for completion - Luma is typically faster than MiniMax
        max_attempts = 30  # Luma usually completes in 2-5 minutes
        attempt = 0
        
        while attempt < max_attempts:
            time.sleep(8)  # Faster polling for better UX
            attempt += 1
            
            status_url = f"{self.base_url}/{generation_id}"
            status_response = requests.get(status_url, headers=self.headers)
            
            if status_response.status_code != 200:
                print(f"Warning: Luma status check failed: {status_response.status_code}")
                continue
            
            status_data = status_response.json()
            state = status_data.get("state", "unknown")
            
            print(f"Luma generation {generation_id} status: {state} (attempt {attempt}/{max_attempts})")
            
            if state == "completed":
                video_url = status_data.get("assets", {}).get("video")
                if video_url:
                    print(f"Luma video generation completed! URL: {video_url}")
                    return video_url
                else:
                    raise Exception("Generation completed but no video URL found")
            
            elif state in ["failed", "error"]:
                error_msg = status_data.get("failure_reason", "Unknown error")
                raise Exception(f"Luma video generation failed: {error_msg}")
        
        raise Exception(f"Luma video generation timed out after {max_attempts} attempts")
    
    def download_video(self, video_url: str, output_path: str, max_retries: int = 3) -> bool:
        """Download video from URL to local file."""
        for attempt in range(max_retries):
            try:
                print(f"Downloading Luma video (attempt {attempt + 1}/{max_retries})...")
                
                response = requests.get(video_url, stream=True, timeout=120)
                response.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    total_size = 0
                    for chunk in response.iter_content(chunk_size=16384):
                        if chunk:
                            f.write(chunk)
                            total_size += len(chunk)
                
                print(f"Downloaded {total_size:,} bytes")
                
                if total_size > 100000:  # Basic validation
                    print(f"Video download successful!")
                    return True
                else:
                    print(f"Downloaded file too small, retrying...")
                    continue
                
            except Exception as e:
                print(f"Download attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
        
        print(f"All {max_retries} download attempts failed")
        return False
    
    def text_to_video(self, prompt: str, aspect_ratio: str = "9:16") -> str:
        """Text to video generation."""
        return self.generate_video(prompt, aspect_ratio, image_url=None)
    
    def image_to_video(self, prompt: str, image_url: str, aspect_ratio: str = "9:16") -> str:
        """Image to video generation."""
        return self.generate_video(prompt, aspect_ratio, image_url=image_url)
