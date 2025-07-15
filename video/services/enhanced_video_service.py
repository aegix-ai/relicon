"""Enhanced video service with captions, human-like audio, and dynamic scenes"""
import time
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from config.settings import settings
from video.caption.caption_generator import caption_generator
from video.audio.enhanced_audio_processor import enhanced_audio_processor
from video.scenes.dynamic_scene_planner import dynamic_scene_planner
from ai.planners.video_planner import video_planner

class EnhancedVideoService:
    """Enhanced video service with advanced features"""
    
    def __init__(self):
        self.output_dir = Path(settings.OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "temp").mkdir(exist_ok=True)
        (self.output_dir / "scenes").mkdir(exist_ok=True)
        (self.output_dir / "audio").mkdir(exist_ok=True)
    
    def create_enhanced_video(self, brand_info: Dict[str, Any], 
                            progress_callback=None) -> Dict[str, Any]:
        """Create enhanced video with captions, human audio, and dynamic scenes"""
        try:
            if progress_callback:
                progress_callback(5, "Planning enhanced video experience...")
            
            # Step 1: Create comprehensive video plan
            master_plan = video_planner.create_master_plan(brand_info)
            if not master_plan.get("success"):
                return {"success": False, "error": "Failed to create video plan"}
            
            if progress_callback:
                progress_callback(15, "Generating human-like script...")
            
            # Step 2: Generate script segments
            script_segments = self._generate_enhanced_script(brand_info, master_plan)
            if not script_segments:
                return {"success": False, "error": "Failed to generate script"}
            
            if progress_callback:
                progress_callback(25, "Creating natural human voiceover...")
            
            # Step 3: Generate human-like audio
            audio_file = self._create_human_audio(script_segments, brand_info)
            if not audio_file:
                print("Enhanced audio failed, creating fallback audio...")
                audio_file = self._create_fallback_audio(script_segments, brand_info)
                if not audio_file:
                    return {"success": False, "error": "Failed to generate audio"}
            
            if progress_callback:
                progress_callback(35, "Planning dynamic visual scenes...")
            
            # Step 4: Plan dynamic scenes
            scene_plans = dynamic_scene_planner.plan_scene_components(script_segments, brand_info)
            if not scene_plans:
                return {"success": False, "error": "Failed to plan scenes"}
            
            if progress_callback:
                progress_callback(45, "Creating colorful dynamic backgrounds...")
            
            # Step 5: Create dynamic scene backgrounds
            scene_videos = self._create_scene_backgrounds(scene_plans)
            
            if progress_callback:
                progress_callback(60, "Generating synchronized captions...")
            
            # Step 6: Generate captions
            caption_segments = caption_generator.generate_captions(script_segments, audio_file)
            
            if progress_callback:
                progress_callback(75, "Assembling final video with captions...")
            
            # Step 7: Assemble final video
            final_video = self._assemble_enhanced_video(
                scene_videos, audio_file, caption_segments, brand_info
            )
            
            if progress_callback:
                progress_callback(100, "Enhanced video creation complete!")
            
            if final_video:
                return {
                    "success": True,
                    "video_path": final_video,
                    "video_url": f"/outputs/{os.path.basename(final_video)}",
                    "duration": brand_info.get("duration", 30),
                    "type": "enhanced",
                    "features": ["captions", "human_audio", "dynamic_scenes"],
                    "master_plan": master_plan
                }
            else:
                return {"success": False, "error": "Failed to assemble video"}
                
        except Exception as e:
            return {"success": False, "error": f"Enhanced video creation failed: {str(e)}"}
    
    def _generate_enhanced_script(self, brand_info: Dict[str, Any], 
                                master_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate enhanced script with natural human speech patterns"""
        try:
            from ai.agents.script_generator import script_generator
            
            # Get base script
            base_segments = script_generator.generate_energetic_segments(brand_info, 3)
            
            # Enhance for human-like speech
            enhanced_segments = []
            for i, segment in enumerate(base_segments):
                enhanced_text = self._humanize_script_text(segment["text"])
                
                enhanced_segments.append({
                    "index": i,
                    "text": enhanced_text,
                    "duration": segment.get("duration", 10),
                    "tone": "conversational",
                    "energy": "natural"
                })
            
            return enhanced_segments
            
        except Exception as e:
            print(f"Enhanced script generation error: {e}")
            return []
    
    def _humanize_script_text(self, text: str) -> str:
        """Make script text more natural and human-like"""
        # Remove overly promotional language
        humanized = text.replace("revolutionary", "great")
        humanized = humanized.replace("amazing", "really good")
        humanized = humanized.replace("incredible", "impressive")
        
        # Add natural speech patterns
        humanized = humanized.replace("!", ".")
        humanized = humanized.replace("?", ".")
        
        # Add conversational elements
        if not humanized.startswith(("So", "Well", "Now", "You know")):
            humanized = "So " + humanized
        
        # Make it sound more casual
        humanized = humanized.replace("you will", "you'll")
        humanized = humanized.replace("it is", "it's")
        humanized = humanized.replace("we are", "we're")
        
        return humanized
    
    def _create_human_audio(self, script_segments: List[Dict[str, Any]], 
                          brand_info: Dict[str, Any]) -> Optional[str]:
        """Create human-like audio from script segments"""
        try:
            # Combine all text
            full_text = " ".join([segment["text"] for segment in script_segments])
            
            # Determine voice style based on brand
            voice_style = self._determine_voice_style(brand_info)
            
            # Generate human-like voiceover
            audio_file = enhanced_audio_processor.create_human_voiceover(full_text, voice_style)
            
            return audio_file
            
        except Exception as e:
            print(f"Human audio creation error: {e}")
            return None
    
    def _determine_voice_style(self, brand_info: Dict[str, Any]) -> str:
        """Determine voice style based on brand information"""
        brand_style = brand_info.get("style", "professional").lower()
        
        style_mapping = {
            "professional": "professional",
            "casual": "conversational",
            "friendly": "warm",
            "energetic": "natural",
            "corporate": "professional"
        }
        
        return style_mapping.get(brand_style, "natural")
    
    def _create_scene_backgrounds(self, scene_plans: List[Dict[str, Any]]) -> List[str]:
        """Create dynamic background videos for each scene"""
        scene_videos = []
        
        for scene_plan in scene_plans:
            try:
                output_path = self.output_dir / "scenes" / f"scene_{scene_plan['index']}.mp4"
                
                success = dynamic_scene_planner.create_dynamic_background(
                    scene_plan, str(output_path)
                )
                
                if success and output_path.exists():
                    scene_videos.append(str(output_path))
                else:
                    # Fallback: create simple colored background
                    fallback_path = self._create_fallback_background(scene_plan)
                    if fallback_path:
                        scene_videos.append(fallback_path)
                        
            except Exception as e:
                print(f"Scene background creation error: {e}")
                # Create fallback
                fallback_path = self._create_fallback_background(scene_plan)
                if fallback_path:
                    scene_videos.append(fallback_path)
        
        return scene_videos
    
    def _create_fallback_background(self, scene_plan: Dict[str, Any]) -> Optional[str]:
        """Create fallback colored background"""
        try:
            import subprocess
            
            colors = scene_plan.get("color_palette", ["#1a1a2e"])
            duration = scene_plan.get("duration", 5)
            
            output_path = self.output_dir / "scenes" / f"fallback_{scene_plan['index']}.mp4"
            
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", f"color=c={colors[0].replace('#', '0x')}:s=1920x1080:d={duration}",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return str(output_path)
            
            return None
            
        except Exception as e:
            print(f"Fallback background creation error: {e}")
            return None
    
    def _assemble_enhanced_video(self, scene_videos: List[str], audio_file: str, 
                               caption_segments: List[Dict[str, Any]], 
                               brand_info: Dict[str, Any]) -> Optional[str]:
        """Assemble final video with scenes, audio, and captions"""
        try:
            import subprocess
            
            # Create temporary video without captions
            temp_video = self.output_dir / "temp" / f"temp_{int(time.time())}.mp4"
            
            if scene_videos:
                # Concatenate scene videos
                success = self._concatenate_scenes(scene_videos, str(temp_video))
                if not success:
                    return None
            else:
                # Create simple background video
                duration = brand_info.get("duration", 30)
                cmd = [
                    "ffmpeg", "-y",
                    "-f", "lavfi",
                    "-i", f"color=c=0x1a1a2e:s=1920x1080:d={duration}",
                    "-c:v", "libx264",
                    str(temp_video)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    return None
            
            # Add audio to video
            video_with_audio = self.output_dir / "temp" / f"with_audio_{int(time.time())}.mp4"
            
            cmd = [
                "ffmpeg", "-y",
                "-i", str(temp_video),
                "-i", audio_file,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                str(video_with_audio)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return None
            
            # Add captions
            final_output = self.output_dir / f"enhanced_{brand_info.get('brand_name', 'video')}_{int(time.time())}.mp4"
            
            if caption_segments:
                success = caption_generator.add_captions_to_video(
                    str(video_with_audio), caption_segments, str(final_output)
                )
                
                if success:
                    return str(final_output)
            
            # If captions fail, return video with audio
            import shutil
            shutil.move(str(video_with_audio), str(final_output))
            return str(final_output)
            
        except Exception as e:
            print(f"Video assembly error: {e}")
            return None
    
    def _concatenate_scenes(self, scene_videos: List[str], output_path: str) -> bool:
        """Concatenate scene videos into single video"""
        try:
            import subprocess
            
            if len(scene_videos) == 1:
                # Single video, just copy
                import shutil
                shutil.copy2(scene_videos[0], output_path)
                return True
            
            # Create concat list file
            concat_file = self.output_dir / "temp" / "concat_list.txt"
            
            with open(concat_file, 'w') as f:
                for video in scene_videos:
                    f.write(f"file '{video}'\n")
            
            # Concatenate videos
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-c", "copy",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up
            if concat_file.exists():
                concat_file.unlink()
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Video concatenation error: {e}")
            return False
    
    def _create_fallback_audio(self, script_segments: List[Dict[str, Any]], 
                             brand_info: Dict[str, Any]) -> Optional[str]:
        """Create fallback audio using OpenAI TTS"""
        try:
            from openai import OpenAI
            import time
            
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Combine all text
            full_text = " ".join([segment["text"] for segment in script_segments])
            
            # Generate audio with OpenAI
            response = client.audio.speech.create(
                model="tts-1-hd",
                voice="alloy",
                input=full_text,
                speed=0.85  # Slower for more natural delivery
            )
            
            output_file = self.output_dir / "audio" / f"fallback_{int(time.time())}.mp3"
            response.stream_to_file(output_file)
            
            return str(output_file)
            
        except Exception as e:
            print(f"Fallback audio creation error: {e}")
            return None

# Global instance
enhanced_video_service = EnhancedVideoService()