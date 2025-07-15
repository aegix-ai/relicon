"""
Core video generation service
Orchestrates the complete video generation pipeline
"""
import os
import sys
import tempfile
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from config.settings import settings
from ai.planners import video_planner, script_generator
from video.generation import video_generator, audio_processor
from external.apis import luma_client, openai_client

class VideoService:
    """Main service for orchestrating video generation"""
    
    def __init__(self):
        self.planner = video_planner
        self.script_gen = script_generator
        self.video_gen = video_generator
        self.audio_proc = audio_processor
        self.luma = luma_client
        self.openai = openai_client
        
        # Ensure output directory exists
        self.output_dir = Path(settings.OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_video(self, brand_info: Dict[str, Any], 
                      progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Generate complete video from brand information
        
        Args:
            brand_info: Brand information including name, description, duration, etc.
            progress_callback: Optional callback for progress updates
            
        Returns:
            dict: Generation result with video path or error information
        """
        try:
            if progress_callback:
                progress_callback(5, "Starting video generation pipeline...")
            
            # Step 1: Create master plan
            master_plan = self.planner.create_master_plan(brand_info)
            if not master_plan.get("success"):
                return {"success": False, "error": "Failed to create master plan"}
            
            if progress_callback:
                progress_callback(15, "Master plan created, breaking down scenes...")
            
            # Step 2: Break down into scenes
            duration = brand_info.get("duration", settings.DEFAULT_VIDEO_DURATION)
            scenes = self.planner.break_down_components(master_plan, duration)
            
            if progress_callback:
                progress_callback(25, "Generating scripts for each scene...")
            
            # Step 3: Generate scripts for each scene
            script_segments = self.script_gen.generate_energetic_segments(
                brand_info, len(scenes)
            )
            
            if progress_callback:
                progress_callback(35, "Creating voiceovers...")
            
            # Step 4: Generate voiceovers
            audio_segments = []
            for i, segment in enumerate(script_segments):
                audio_file = self.audio_proc.create_advertisement_voiceover(
                    segment["text"], voice="alloy"
                )
                if audio_file:
                    audio_segments.append({
                        "index": i,
                        "audio_file": audio_file,
                        "duration": segment.get("duration", 5),
                        "text": segment["text"]
                    })
            
            if not audio_segments:
                return {"success": False, "error": "Failed to generate audio segments"}
            
            if progress_callback:
                progress_callback(50, "Generating visual content...")
            
            # Step 5: Generate visual content (optional Luma videos)
            video_segments = []
            for i, (scene, audio_seg) in enumerate(zip(scenes, audio_segments)):
                segment = {
                    "index": i,
                    "audio_file": audio_seg["audio_file"],
                    "duration": audio_seg["duration"],
                    "visual_type": "color",  # Default to simple color background
                    "background_color": "#1a1a2e"
                }
                
                # Try to generate Luma video if enabled
                if settings.LUMA_API_KEY and scene.get("type") != "cta":
                    luma_video = self._generate_luma_video(scene, brand_info)
                    if luma_video:
                        segment["visual_type"] = "luma_video"
                        segment["luma_video_file"] = luma_video
                
                video_segments.append(segment)
            
            if progress_callback:
                progress_callback(70, "Assembling final video...")
            
            # Step 6: Assemble final video
            output_filename = f"{brand_info.get('brand_name', 'video')}_{int(time.time())}.mp4"
            output_path = self.output_dir / output_filename
            
            success = self.video_gen.create_video_from_segments(
                video_segments, 
                str(output_path), 
                progress_callback
            )
            
            if success and self.video_gen.validate_video(str(output_path)):
                if progress_callback:
                    progress_callback(100, "Video generation complete!")
                
                return {
                    "success": True,
                    "video_path": str(output_path),
                    "video_url": f"/outputs/{output_filename}",
                    "duration": duration,
                    "segments": len(video_segments),
                    "master_plan": master_plan
                }
            else:
                return {"success": False, "error": "Failed to create final video"}
                
        except Exception as e:
            error_msg = f"Video generation failed: {str(e)}"
            print(error_msg)
            return {"success": False, "error": error_msg}
    
    def _generate_luma_video(self, scene: Dict[str, Any], 
                           brand_info: Dict[str, Any]) -> Optional[str]:
        """Generate Luma video for a scene"""
        try:
            # Create video prompt based on scene
            prompt = self._create_luma_prompt(scene, brand_info)
            
            # Generate video
            job_id = self.luma.generate_video(prompt, duration=5)
            if not job_id:
                return None
            
            # Wait for completion
            video_url = self.luma.wait_for_completion(job_id, max_wait=180)
            if not video_url:
                return None
            
            # Download video
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
                temp_path = f.name
            
            if self.luma.download_video(video_url, temp_path):
                return temp_path
            
            return None
            
        except Exception as e:
            print(f"Error generating Luma video: {e}")
            return None
    
    def _create_luma_prompt(self, scene: Dict[str, Any], 
                          brand_info: Dict[str, Any]) -> str:
        """Create optimized prompt for Luma video generation"""
        scene_type = scene.get("type", "generic")
        visual_style = scene.get("visual_style", "professional")
        brand_name = brand_info.get("brand_name", "product")
        
        prompt_templates = {
            "hook": f"Dynamic opening scene showcasing {brand_name} with {visual_style} style, attention-grabbing visuals, modern aesthetic",
            "problem": f"Relatable problem scenario, frustrated person, everyday situation, {visual_style} lighting",
            "solution": f"Product demonstration of {brand_name}, clean presentation, {visual_style} style, transformation moment",
            "benefits": f"Happy customer using {brand_name}, positive transformation, {visual_style} aesthetic, aspirational lifestyle",
            "cta": f"Clear call-to-action visual, {brand_name} branding, {visual_style} design, compelling final frame"
        }
        
        base_prompt = prompt_templates.get(scene_type, f"Professional {brand_name} commercial scene")
        
        # Add quality modifiers
        quality_modifiers = [
            "high quality",
            "professional lighting",
            "sharp focus",
            "commercial grade",
            "smooth motion"
        ]
        
        return f"{base_prompt}, {', '.join(quality_modifiers)}"
    
    def create_simple_video(self, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a simple video without Luma AI (faster generation)"""
        try:
            # Generate script
            script_segments = self.script_gen.generate_energetic_segments(brand_info, 1)
            if not script_segments:
                return {"success": False, "error": "Failed to generate script"}
            
            # Generate voiceover
            audio_file = self.audio_proc.create_advertisement_voiceover(
                script_segments[0]["text"]
            )
            if not audio_file:
                return {"success": False, "error": "Failed to generate voiceover"}
            
            # Create simple video
            duration = brand_info.get("duration", 30)
            output_filename = f"{brand_info.get('brand_name', 'video')}_{int(time.time())}.mp4"
            output_path = self.output_dir / output_filename
            
            segments = [{
                "index": 0,
                "audio_file": audio_file,
                "duration": duration,
                "visual_type": "color",
                "background_color": "#1a1a2e"
            }]
            
            video_path = self.video_gen.create_simple_video(brand_info, [audio_file])
            success = video_path is not None
            
            if success and video_path:
                return {
                    "success": True,
                    "video_path": video_path,
                    "video_url": f"/outputs/{os.path.basename(video_path)}",
                    "duration": duration,
                    "type": "simple"
                }
            else:
                return {"success": False, "error": "Failed to create video"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_generation_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of video generation job"""
        # This would integrate with a job queue system
        # For now, return basic status
        return {
            "job_id": job_id,
            "status": "completed",
            "progress": 100
        }

# Global video generation service
video_service = VideoService()

# Legacy functions for backwards compatibility
def create_enhanced_video_generation(brand_info: Dict[str, Any], 
                                   output_file: str) -> bool:
    """Legacy function for video generation"""
    result = video_service.generate_video(brand_info)
    if result.get("success") and result.get("video_path"):
        # Copy to requested output file
        import shutil
        shutil.copy2(result["video_path"], output_file)
        return True
    return False

def progress_update(progress: int, message: str):
    """Legacy progress update function"""
    print(f"Progress: {progress}% - {message}")

def make_advertisement_energetic(text: str) -> str:
    """Legacy function for making text energetic"""
    return script_generator.enhance_script_energy(text)

def enhance_audio_energy(input_file: str, output_file: str) -> bool:
    """Legacy function for enhancing audio"""
    return audio_processor.enhance_audio_energy(input_file, output_file)