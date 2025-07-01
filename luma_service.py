"""
Luma AI Video Generation Service
Intelligent video planning and generation using Luma AI
"""
import os
import json
import time
import requests
from typing import List, Dict, Any, Optional

class LumaVideoService:
    def __init__(self):
        self.api_key = os.environ.get("LUMA_API_KEY")
        if not self.api_key:
            raise ValueError("LUMA_API_KEY environment variable is required")
        
        self.base_url = "https://api.lumalabs.ai/dream-machine/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def plan_video_segments(self, script_segments: List[Dict[str, Any]], total_duration: int = 30) -> List[Dict[str, Any]]:
        """
        Intelligently plan video segments based on script content
        Creates optimal combinations like 3x10s, 1x10s+2x5s, etc.
        """
        num_segments = len(script_segments)
        
        # Intelligent segment duration planning
        if num_segments <= 3:
            # For 1-3 segments: use longer durations (10s each)
            segment_duration = min(10, total_duration // num_segments)
        elif num_segments <= 5:
            # For 4-5 segments: use medium durations (6-8s each)
            segment_duration = min(8, total_duration // num_segments)
        else:
            # For 6+ segments: use shorter durations (5s each)
            segment_duration = min(5, total_duration // num_segments)
        
        # Ensure we don't exceed total duration
        if segment_duration * num_segments > total_duration:
            segment_duration = total_duration // num_segments
        
        planned_segments = []
        for i, segment in enumerate(script_segments):
            # Create visual prompt based on script content
            visual_prompt = self._create_visual_prompt(segment["voiceover"], i)
            
            planned_segments.append({
                "index": i,
                "duration": segment_duration,
                "voiceover": segment["voiceover"],
                "visual_prompt": visual_prompt,
                "aspect_ratio": "9:16"  # TikTok/Instagram format
            })
        
        return planned_segments
    
    def _create_visual_prompt(self, voiceover_text: str, scene_index: int) -> str:
        """
        Create optimized visual prompts for Luma AI based on voiceover content
        """
        # Extract key concepts from voiceover
        text_lower = voiceover_text.lower()
        
        # Scene type detection
        if any(word in text_lower for word in ["product", "item", "buy", "shop", "sale"]):
            scene_type = "product showcase"
        elif any(word in text_lower for word in ["person", "people", "customer", "user"]):
            scene_type = "lifestyle scene"
        elif any(word in text_lower for word in ["brand", "company", "business"]):
            scene_type = "brand identity"
        else:
            scene_type = "abstract concept"
        
        # Visual style based on content
        if "luxury" in text_lower or "premium" in text_lower:
            style = "cinematic, luxury lighting, premium aesthetic"
        elif "tech" in text_lower or "digital" in text_lower:
            style = "modern, sleek, tech-forward"
        elif "natural" in text_lower or "organic" in text_lower:
            style = "natural lighting, organic feel"
        else:
            style = "professional, clean, engaging"
        
        # Camera movement for dynamic feel
        movements = [
            "smooth camera push in",
            "elegant camera rotation",
            "subtle camera pull back",
            "dynamic camera slide"
        ]
        movement = movements[scene_index % len(movements)]
        
        return f"{scene_type}, {style}, {movement}, 9:16 aspect ratio, high quality"
    
    def generate_video_segment(self, prompt: str, duration: int = 5) -> Optional[str]:
        """
        Generate a single video segment using Luma AI
        Returns the generation job ID
        """
        try:
            payload = {
                "prompt": prompt,
                "aspect_ratio": "9:16",
                "duration": duration,
                "loop": False
            }
            
            response = requests.post(
                f"{self.base_url}/generations",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                return result.get("id")
            else:
                print(f"Luma API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error generating video segment: {e}")
            return None
    
    def check_generation_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check the status of a video generation job
        """
        try:
            response = requests.get(
                f"{self.base_url}/generations/{job_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"state": "failed", "error": f"API error: {response.status_code}"}
                
        except Exception as e:
            return {"state": "failed", "error": str(e)}
    
    def wait_for_completion(self, job_id: str, max_wait: int = 300) -> Optional[str]:
        """
        Wait for video generation to complete and return download URL
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = self.check_generation_status(job_id)
            state = status.get("state", "unknown")
            
            if state == "completed":
                # Return the video URL
                assets = status.get("assets", {})
                return assets.get("video")
            elif state == "failed":
                print(f"Video generation failed: {status.get('failure_reason', 'Unknown error')}")
                return None
            
            # Wait before checking again
            time.sleep(10)
        
        print(f"Video generation timeout after {max_wait} seconds")
        return None
    
    def download_video(self, video_url: str, output_path: str) -> bool:
        """
        Download generated video to local file
        """
        try:
            response = requests.get(video_url, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return os.path.exists(output_path) and os.path.getsize(output_path) > 0
            
        except Exception as e:
            print(f"Error downloading video: {e}")
            return False
    
    def generate_multiple_segments(self, planned_segments: List[Dict[str, Any]], progress_callback=None) -> List[str]:
        """
        Generate multiple video segments efficiently
        """
        job_ids = []
        video_files = []
        
        # Start all generations in parallel
        for i, segment in enumerate(planned_segments):
            if progress_callback:
                progress_callback(60 + (i * 5), f"Starting video generation for segment {i+1}")
            
            job_id = self.generate_video_segment(
                segment["visual_prompt"], 
                segment["duration"]
            )
            
            if job_id:
                job_ids.append((job_id, segment, i))
            else:
                print(f"Failed to start generation for segment {i}")
        
        # Wait for completions and download
        for job_id, segment, index in job_ids:
            if progress_callback:
                progress_callback(70 + (index * 3), f"Processing video segment {index+1}")
            
            video_url = self.wait_for_completion(job_id)
            if video_url:
                output_path = f"/tmp/luma_segment_{index}.mp4"
                if self.download_video(video_url, output_path):
                    video_files.append(output_path)
                else:
                    print(f"Failed to download segment {index}")
            else:
                print(f"Generation failed for segment {index}")
        
        return video_files