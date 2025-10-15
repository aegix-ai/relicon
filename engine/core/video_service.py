"""
  High-level video generation service.
  Orchestrates video creation using abstracted providers.
"""

import os
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from core.provider_manager import provider_manager
from core.logger import video_logger
from config.settings import settings


class VideoService:
    """High-level video generation orchestration service."""
    
    def __init__(self):
        self.provider_manager = provider_manager
    
    def generate_video_from_architecture(self, architecture: Dict[str, Any], output_dir: str, 
                                       progress_callback: callable = None) -> Dict[str, Any]:
        """
        Generate complete video from architectural plan.
        
        Args:
            architecture: Video architecture from planning service
            output_dir: Directory to save generated videos
            
        Returns:
            Dictionary with generation results and file paths
        """
        scenes = architecture.get('scene_architecture', {}).get('scenes', [])
        if not scenes:
            raise ValueError("No scenes found in architecture")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate video for each scene
        video_logger.video_generation_start(
            job_id=architecture.get('job_id', 'unknown'),
            provider=self.provider_manager.get_video_generator().__class__.__name__,
            prompt_length=len(str(scenes))
        )
        generated_videos = []
        video_generator = self.provider_manager.get_video_generator()
        
        for i, scene in enumerate(scenes):
            scene_number = i + 1
            print(f"Generating scene {scene_number}/{len(scenes)}: {scene.get('purpose', 'Unknown')}")
            
            # Update progress for each scene (25% to 70% divided by number of scenes)
            scene_progress = 25 + int((45 / len(scenes)) * i)
            if progress_callback:
                progress_callback(scene_progress, f"Generating Scene {scene_number}/{len(scenes)}...")
            
            # Get appropriate prompt based on provider
            provider_name = getattr(settings, 'VIDEO_PROVIDER', 'hailuo').lower()
            if provider_name == 'hailuo':
                prompt = scene.get('hailuo_prompt', scene.get('visual_concept', ''))
            else:
                prompt = scene.get('luma_prompt', scene.get('visual_concept', ''))
            
            if not prompt:
                print(f"Warning: No prompt found for scene {scene_number}")
                continue
            
            try:
                # Generate video with primary provider
                video_url = video_generator.generate_video(
                    prompt=prompt,
                    aspect_ratio="9:16",
                    force_unique=True
                )
                
                # Download video
                output_filename = f"scene_{scene_number:02d}_{int(time.time())}.mp4"
                output_path = os.path.join(output_dir, output_filename)
                
                if video_generator.download_video(video_url, output_path):
                    generated_videos.append({
                        'scene_number': scene_number,
                        'file_path': output_path,
                        'duration': scene.get('duration', 5),
                        'prompt': prompt,
                        'url': video_url
                    })
                    print(f"Scene {scene_number} completed: {output_filename}")
                    
                    # Update progress after scene completion
                    scene_complete_progress = 25 + int((45 / len(scenes)) * (i + 1))
                    if progress_callback:
                        progress_callback(scene_complete_progress, f"Scene {scene_number}/{len(scenes)} completed")
                else:
                    print(f"Failed to download scene {scene_number}")
                    
            except Exception as e:
                print(f"Scene {scene_number} generation failed: {e}")
                
                # Try fallback to Luma if primary provider fails or times out
                if provider_name == 'hailuo':
                    try:
                        print(f"Attempting fallback to Luma for scene {scene_number}...")
                        from providers.luma import LumaProvider
                        fallback_generator = LumaProvider()
                        
                        fallback_prompt = scene.get('luma_prompt', scene.get('visual_concept', ''))
                        if fallback_prompt:
                            video_url = fallback_generator.generate_video(
                                prompt=fallback_prompt,
                                aspect_ratio="9:16"
                            )
                            
                            output_filename = f"scene_{scene_number:02d}_luma_{int(time.time())}.mp4"
                            output_path = os.path.join(output_dir, output_filename)
                            
                            if fallback_generator.download_video(video_url, output_path):
                                generated_videos.append({
                                    'scene_number': scene_number,
                                    'file_path': output_path,
                                    'duration': scene.get('duration', 5),
                                    'prompt': fallback_prompt,
                                    'url': video_url,
                                    'provider': 'luma_fallback'
                                })
                                print(f"Scene {scene_number} completed with Luma fallback: {output_filename}")
                            else:
                                print(f"Fallback also failed to download scene {scene_number}")
                    except Exception as fallback_error:
                        print(f"Fallback to Luma also failed: {fallback_error}")
                continue
        
        return {
            'total_scenes': len(scenes),
            'generated_scenes': len(generated_videos),
            'videos': generated_videos,
            'success_rate': len(generated_videos) / len(scenes) if scenes else 0
        }
    
    def generate_single_video(self, prompt: str, output_path: str, **kwargs) -> bool:
        """
        Generate a single video from prompt.
        
        Args:
            prompt: Text description for video
            output_path: Local path to save video
            **kwargs: Additional parameters
            
        Returns:
            True if successful, False otherwise
        """
        try:
            video_generator = self.provider_manager.get_video_generator()
            
            video_url = video_generator.generate_video(
                prompt=prompt,
                aspect_ratio=kwargs.get('aspect_ratio', '9:16'),
                image_url=kwargs.get('image_url'),
                **kwargs
            )
            
            return video_generator.download_video(video_url, output_path)
            
        except Exception as e:
            print(f"Single video generation failed: {e}")
            return False
    
    def switch_provider(self, provider_name: str) -> None:
        """
        Switch video generation provider at runtime.
        
        Args:
            provider_name: Name of the provider ('hailuo', 'luma', etc.)
        """
        try:
            self.provider_manager.set_video_provider(provider_name)
            print(f"Switched to {provider_name} video provider")
        except Exception as e:
            print(f"Failed to switch to {provider_name}: {e}")
            raise
