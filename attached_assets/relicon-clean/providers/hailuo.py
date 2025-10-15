"""
  Hailuo (MiniMax) video generation provider implementation.
"""

import os
import requests
import time
import base64
import json
import subprocess
from typing import Dict, Any, Optional
from interfaces.video_generator import VideoGenerator


class HailuoProvider(VideoGenerator):
    """Hailuo (MiniMax) video generation service implementation."""
    
    def __init__(self):
        self.api_key = os.environ.get("HAILUO_API_KEY")
        if not self.api_key:
            raise ValueError("HAILUO_API_KEY environment variable is required")
        
        # Extract GroupID from JWT for official MiniMax API
        self.group_id = None
        try:
            parts = self.api_key.split('.')
            payload_b64 = parts[1] + '=' * (4 - len(parts[1]) % 4)
            payload = json.loads(base64.b64decode(payload_b64))
            self.group_id = payload.get('GroupID')
        except:
            pass
            
        # Official MiniMax API configuration
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
            
        self.api_endpoints = [
            {
                "name": "MiniMax Official API",
                "base_url": "https://api.minimax.io/v1/video_generation",
                "query_url": "https://api.minimax.io/v1/query/video_generation",
                "headers": headers
            }
        ]
        
        self.current_endpoint = None
        
    def _test_endpoint(self, endpoint: Dict[str, Any]) -> bool:
        """Test if MiniMax API endpoint is working."""
        try:
            query_url = endpoint.get("query_url", endpoint["base_url"])
            response = requests.get(query_url, headers=endpoint["headers"], timeout=10)
            return response.status_code in [200, 201, 202]
        except:
            return False
    
    def _get_working_endpoint(self) -> Dict[str, Any]:
        """Find and return a working API endpoint."""
        if self.current_endpoint:
            return self.current_endpoint
            
        for endpoint in self.api_endpoints:
            print(f"Testing {endpoint['name']} endpoint...")
            if self._test_endpoint(endpoint):
                self.current_endpoint = endpoint
                print(f"✓ Using {endpoint['name']} for video generation")
                return endpoint
                
        # Fallback to first endpoint if none test successful
        self.current_endpoint = self.api_endpoints[0]
        print(f"⚠ Using fallback endpoint: {self.current_endpoint['name']}")
        return self.current_endpoint
    
    def generate_video(self, prompt: str, aspect_ratio: str = "9:16", 
                      image_url: Optional[str] = None, **kwargs) -> str:
        """Generate video using Hailuo-02 model."""
        endpoint = self._get_working_endpoint()
        
        # Apply cinematic enhancement for incredible realism
        force_unique = kwargs.get('force_unique', True)
        if force_unique:
            import random
            
            # Modern commercial cinematography elements
            cinematography_elements = [
                "professional commercial cinematography with dynamic product focus",
                "cinematic depth of field highlighting product details",
                "golden hour lighting showcasing product aesthetics",
                "commercial-grade color grading emphasizing brand colors",
                "high-end product photography lighting setup",
                "sleek modern commercial visual style"
            ]
            
            # Product-focused camera work
            camera_work = [
                "dynamic product reveal shots with smooth camera movement",
                "macro close-ups highlighting product features and details", 
                "wide lifestyle shots showing product in natural environment",
                "tracking shots following product usage and interaction",
                "rotating product shots showcasing all angles and benefits",
                "overhead shots capturing product workflow and process"
            ]
            
            # Environmental and lifestyle elements
            environment_lifestyle = [
                "modern lifestyle environments showcasing product integration",
                "authentic real-world settings where product is naturally used",
                "clean professional environments highlighting product quality",
                "dynamic action scenes demonstrating product benefits",
                "atmospheric product placement in aspirational settings"
            ]
            
            # Action and demonstration focus
            action_demonstration = [
                "hands-on product demonstration showing clear benefits",
                "before-and-after transformation scenes highlighting results",
                "product solving real problems through visual demonstration",
                "lifestyle improvement through product integration",
                "seamless product workflow and ease of use display",
                "clear product branding and visual identity integration"
            ]
            
            # Technical and visual quality
            technical_quality = [
                "8K ultra-realistic product detail with photographic quality",
                "professional lighting highlighting product textures and materials",
                "crisp focus on product functionality and design elements",
                "commercial-grade visual polish with premium aesthetics",
                "realistic product physics and natural interaction"
            ]
            
            # Select elements for maximum modern commercial impact
            selected_elements = [
                random.choice(cinematography_elements),
                random.choice(camera_work),
                random.choice(environment_lifestyle),
                random.choice(action_demonstration),
                random.choice(technical_quality),
                f"seed_{random.randint(10000, 99999)}",
                "modern commercial advertisement with product focus"
            ]
            
            enhanced_prompt = f"{prompt}, {', '.join(selected_elements)}"
        else:
            enhanced_prompt = prompt
            
        # Official MiniMax API payload - using latest model with 720p cost optimization
        payload = {
            "model": "video-01",
            "prompt": enhanced_prompt,
            "prompt_optimizer": True,
            "duration": 6,  # Optimized for 6s per scene, 3-scene structure
            "resolution": "720p"  # Cost-optimized resolution for $0.4 per 5s
        }
        
        if image_url:
            payload["first_frame_image"] = image_url
            
        generation_url = endpoint["base_url"]
        
        print(f"Starting Hailuo generation with prompt: {prompt[:100]}...")
        
        # Create generation
        response = requests.post(generation_url, json=payload, headers=endpoint["headers"])
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create Hailuo generation: {response.status_code} - {response.text}")
        
        generation_data = response.json()
        print(f"MiniMax API Response: {generation_data}")
        
        # Try multiple possible response formats
        generation_id = (
            generation_data.get("task_id") or 
            generation_data.get("id") or 
            generation_data.get("data", {}).get("task_id") or
            generation_data.get("data", {}).get("id")
        )
        
        if not generation_id:
            print(f"Available keys in response: {list(generation_data.keys())}")
            raise Exception(f"Could not extract task_id from MiniMax response: {generation_data}")
        
        print(f"Hailuo generation started with ID: {generation_id}")
        
        # Poll for completion with timeout (max 5 minutes for enterprise reliability)
        max_attempts = 20  # 20 attempts = ~3.5 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            time.sleep(10)  # 10 seconds between checks
            attempt += 1
            
            status_url = endpoint["query_url"]
            status_params = {"task_id": generation_id}
            status_response = requests.get(status_url, params=status_params, headers=endpoint["headers"])
            
            if status_response.status_code != 200:
                print(f"Warning: Hailuo status check failed: {status_response.status_code}")
                continue
            
            status_data = status_response.json()
            
            # Handle MiniMax status response format
            base_resp = status_data.get("base_resp", {})
            status_code = base_resp.get("status_code")
            actual_status = status_data.get("status", "unknown").lower()
            
            if status_code == 0:
                if actual_status in ["success", "completed", "finished"] and status_data.get("file_id"):
                    state = "completed"
                elif actual_status in ["queueing", "processing", "running", "pending"]:
                    state = "processing"
                else:
                    state = "processing"
            elif status_code in [2013, 1004]:
                state = "failed"
            else:
                state = "processing"
            
            print(f"Hailuo generation {generation_id} status: {state} (attempt {attempt}/{max_attempts}) - {actual_status}")
            
            if state == "completed":
                # Extract video URL from MiniMax response
                video_url = None
                
                if "file_id" in status_data and status_data["file_id"]:
                    file_id = status_data["file_id"]
                    video_url = f"https://api.minimax.io/v1/files/retrieve?file_id={file_id}"
                elif "video_url" in status_data:
                    video_url = status_data["video_url"]
                elif "url" in status_data:
                    video_url = status_data["url"]
                elif "video" in status_data and isinstance(status_data["video"], dict):
                    video_obj = status_data["video"]
                    if "file_id" in video_obj:
                        file_id = video_obj["file_id"]
                        video_url = f"https://api.minimax.io/v1/files/retrieve?file_id={file_id}"
                    elif "url" in video_obj:
                        video_url = video_obj["url"]
                elif "file_url" in status_data:
                    video_url = status_data["file_url"]
                
                if video_url:
                    print(f"Hailuo video generation completed! URL: {video_url}")
                    return video_url
                else:
                    raise Exception("Generation completed but no video URL found")
            
            elif state in ["failed", "error", "failure"]:
                error_msg = status_data.get("error", status_data.get("failure_reason", "Unknown error"))
                raise Exception(f"Hailuo video generation failed: {error_msg}")
        
        raise Exception(f"Hailuo video generation timed out after {max_attempts} attempts (~{max_attempts*10//60} minutes) - will fallback to Luma")
    
    def download_video(self, video_url: str, output_path: str, max_retries: int = 3) -> bool:
        """Download video from URL to local file."""
        for attempt in range(max_retries):
            try:
                print(f"Downloading Hailuo video (attempt {attempt + 1}/{max_retries})...")
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                if self.group_id:
                    headers["GroupId"] = str(self.group_id)
                
                response = requests.get(video_url, headers=headers, timeout=60)
                response.raise_for_status()
                
                content_type = response.headers.get('content-type', '')
                if 'json' in content_type.lower():
                    file_info = response.json()
                    
                    actual_download_url = None
                    if 'file' in file_info:
                        file_data = file_info['file']
                        actual_download_url = file_data.get('download_url') or file_data.get('backup_download_url')
                    elif 'download_url' in file_info:
                        actual_download_url = file_info['download_url']
                        
                    if not actual_download_url:
                        raise Exception(f"No download URL found in response: {file_info}")
                        
                    video_response = requests.get(actual_download_url, stream=True, timeout=120)
                    video_response.raise_for_status()
                    
                    with open(output_path, 'wb') as f:
                        total_size = 0
                        for chunk in video_response.iter_content(chunk_size=16384):
                            if chunk:
                                f.write(chunk)
                                total_size += len(chunk)
                    
                    print(f"Downloaded {total_size:,} bytes")
                    
                    if self._validate_video_file(output_path, total_size):
                        print(f"Video download and validation successful!")
                        return True
                    else:
                        print(f"Video validation failed, retrying...")
                        continue
                        
                else:
                    with open(output_path, 'wb') as f:
                        total_size = 0
                        for chunk in response.iter_content(chunk_size=16384):
                            if chunk:
                                f.write(chunk)
                                total_size += len(chunk)
                    
                    if self._validate_video_file(output_path, total_size):
                        return True
                    else:
                        continue
                
            except Exception as e:
                print(f"Download attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
        
        print(f"All {max_retries} download attempts failed")
        return False
    
    def _validate_video_file(self, file_path: str, file_size: int) -> bool:
        """Validate that downloaded file is a proper video."""
        try:
            if file_size < 100000:
                print(f"File too small: {file_size} bytes")
                return False
            
            cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', 
                   '-show_format', '-show_streams', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                probe_data = json.loads(result.stdout)
                streams = probe_data.get('streams', [])
                video_streams = [s for s in streams if s.get('codec_type') == 'video']
                
                if video_streams:
                    duration = float(probe_data.get('format', {}).get('duration', 0))
                    print(f"✓ Valid video: {duration:.1f}s, {len(video_streams)} video stream(s)")
                    return True
                else:
                    print(f"No video streams found")
                    return False
            else:
                print(f"FFprobe validation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Video validation error: {e}")
            return False
    
    def text_to_video(self, prompt: str, aspect_ratio: str = "9:16") -> str:
        """Text to video generation."""
        return self.generate_video(prompt, aspect_ratio, image_url=None)
    
    def image_to_video(self, prompt: str, image_url: str, aspect_ratio: str = "9:16") -> str:
        """Image to video generation."""
        return self.generate_video(prompt, aspect_ratio, image_url=image_url)
