"""
Improved Video Orchestrator with performance optimizations and reliability
"""

import os
import time
import tempfile
import uuid
import asyncio
from typing import Dict, Any, List, Optional, TypedDict, Annotated, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from core.planning_service import PlanningService
from core.video_service import VideoService
from core.audio_service import AudioService
from core.assembly_service import AssemblyService
from core.cost_tracker import cost_tracker
from core.logger import orchestrator_logger, set_trace_context
from config.settings import settings

logger = logging.getLogger("orchestrator_improved")

class VideoGenerationState(TypedDict):
    """Enhanced state for video generation workflow"""
    brand_info: Dict[str, Any]
    output_path: str
    progress_callback: Optional[Callable[[int, str], None]]
    architecture: Dict[str, Any]
    video_results: Dict[str, Any]
    audio_path: str
    temp_dir: str
    success: bool
    error: Optional[str]
    generation_id: str
    start_time: float
    checkpoints: Dict[str, Any]

class VideoOrchestrator:
    """Enhanced video orchestrator with performance and reliability improvements"""

    def __init__(self):
        self.planning_service = PlanningService()
        self.video_service = VideoService()
        self.audio_service = AudioService()
        self.assembly_service = AssemblyService()
        
        # Performance optimizations
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.cache = {}
        self.generation_stats = {
            "total_generations": 0,
            "successful_generations": 0,
            "average_duration": 0
        }
        
        logger.info("Enhanced video orchestrator initialized")

    def generate_video_ad(
        self,
        brand_name: str,
        brand_description: str,
        product_name: str = "",
        product_description: str = "",
        target_audience: str = "general audience",
        tone: str = "professional",
        duration: int = 18,
        call_to_action: str = "Learn more",
        creative_style: str = "modern",
        progress_callback: Optional[Callable[[int, str], None]] = None,
        product_image_url: Optional[str] = None
    ) -> Optional[str]:
        """
        Enhanced video generation with performance optimizations and better error handling
        """
        generation_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Set trace context for logging
        set_trace_context(generation_id)
        
        try:
            self.generation_stats["total_generations"] += 1
            
            # Initialize progress
            if progress_callback:
                progress_callback(0, "Starting video generation...")
            
            # Create temporary directory with cleanup
            with tempfile.TemporaryDirectory(prefix="relicon_") as temp_dir:
                
                # Initialize state
                state = VideoGenerationState(
                    brand_info={
                        "brand_name": brand_name,
                        "brand_description": brand_description,
                        "product_name": product_name,
                        "product_description": product_description,
                        "target_audience": target_audience,
                        "tone": tone,
                        "duration": duration,
                        "call_to_action": call_to_action,
                        "creative_style": creative_style,
                        "product_image_url": product_image_url
                    },
                    output_path="",
                    progress_callback=progress_callback,
                    architecture={},
                    video_results={},
                    audio_path="",
                    temp_dir=temp_dir,
                    success=False,
                    error=None,
                    generation_id=generation_id,
                    start_time=start_time,
                    checkpoints={}
                )
                
                # Execute generation pipeline with checkpoints
                result = self._execute_pipeline(state)
                
                # Update statistics
                duration_seconds = time.time() - start_time
                if result:
                    self.generation_stats["successful_generations"] += 1
                    
                    # Update average duration
                    total = self.generation_stats["total_generations"]
                    current_avg = self.generation_stats["average_duration"]
                    self.generation_stats["average_duration"] = (
                        (current_avg * (total - 1) + duration_seconds) / total
                    )
                
                logger.info(f"Generation {generation_id} completed in {duration_seconds:.2f}s")
                return result
                
        except Exception as e:
            logger.error(f"Generation {generation_id} failed: {e}", exc_info=True)
            if progress_callback:
                progress_callback(0, f"Generation failed: {str(e)}")
            return None
        finally:
            # Clear trace context
            set_trace_context(None)

    def _execute_pipeline(self, state: VideoGenerationState) -> Optional[str]:
        """Execute the video generation pipeline with enhanced error handling"""
        
        try:
            # Step 1: Planning (10% progress)
            if not self._execute_planning_step(state):
                return None
            
            # Step 2: Parallel video and audio generation (10-80% progress)
            if not self._execute_parallel_generation(state):
                return None
            
            # Step 3: Assembly (80-100% progress)
            return self._execute_assembly_step(state)
            
        except Exception as e:
            state["error"] = str(e)
            logger.error(f"Pipeline execution failed: {e}")
            return None

    def _execute_planning_step(self, state: VideoGenerationState) -> bool:
        """Execute planning step with caching"""
        try:
            if state["progress_callback"]:
                state["progress_callback"](5, "Generating video architecture...")
            
            # Create cache key for planning
            cache_key = self._create_cache_key(state["brand_info"])
            
            # Check cache first
            if cache_key in self.cache:
                logger.info("Using cached architecture")
                state["architecture"] = self.cache[cache_key]
            else:
                # Generate new architecture
                architecture = self.planning_service.create_video_architecture(
                    brand_name=state["brand_info"]["brand_name"],
                    brand_description=state["brand_info"]["brand_description"],
                    product_name=state["brand_info"]["product_name"],
                    product_description=state["brand_info"]["product_description"],
                    target_audience=state["brand_info"]["target_audience"],
                    tone=state["brand_info"]["tone"],
                    duration=state["brand_info"]["duration"],
                    call_to_action=state["brand_info"]["call_to_action"],
                    creative_style=state["brand_info"]["creative_style"]
                )
                
                if not architecture:
                    raise Exception("Failed to generate video architecture")
                
                state["architecture"] = architecture
                
                # Cache the result (limit cache size)
                if len(self.cache) > 100:
                    # Remove oldest entry
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
                
                self.cache[cache_key] = architecture
            
            # Save checkpoint
            state["checkpoints"]["planning"] = {
                "completed": True,
                "timestamp": time.time(),
                "architecture_scenes": len(state["architecture"].get("scenes", []))
            }
            
            if state["progress_callback"]:
                state["progress_callback"](10, "Video architecture created")
            
            return True
            
        except Exception as e:
            logger.error(f"Planning step failed: {e}")
            state["error"] = f"Planning failed: {str(e)}"
            return False

    def _execute_parallel_generation(self, state: VideoGenerationState) -> bool:
        """Execute video and audio generation in parallel for better performance"""
        try:
            if state["progress_callback"]:
                state["progress_callback"](15, "Starting parallel video and audio generation...")
            
            # Prepare futures for parallel execution
            futures = {}
            
            # Submit video generation task
            video_future = self.executor.submit(
                self._generate_videos_with_progress,
                state
            )
            futures["video"] = video_future
            
            # Submit audio generation task
            audio_future = self.executor.submit(
                self._generate_audio_with_progress,
                state
            )
            futures["audio"] = audio_future
            
            # Wait for completion with progress updates
            completed_tasks = set()
            
            while len(completed_tasks) < len(futures):
                for task_name, future in futures.items():
                    if task_name not in completed_tasks and future.done():
                        try:
                            result = future.result()
                            if not result:
                                raise Exception(f"{task_name} generation failed")
                            completed_tasks.add(task_name)
                            logger.info(f"{task_name} generation completed")
                        except Exception as e:
                            logger.error(f"{task_name} generation failed: {e}")
                            return False
                
                # Update overall progress
                progress = 15 + (len(completed_tasks) / len(futures)) * 65
                if state["progress_callback"]:
                    state["progress_callback"](
                        int(progress),
                        f"Generating content... ({len(completed_tasks)}/{len(futures)} tasks complete)"
                    )
                
                time.sleep(0.5)  # Small delay to prevent busy waiting
            
            # Save checkpoint
            state["checkpoints"]["generation"] = {
                "completed": True,
                "timestamp": time.time(),
                "video_scenes": len(state["video_results"]),
                "audio_generated": bool(state["audio_path"])
            }
            
            if state["progress_callback"]:
                state["progress_callback"](80, "Video and audio generation completed")
            
            return True
            
        except Exception as e:
            logger.error(f"Parallel generation failed: {e}")
            state["error"] = f"Generation failed: {str(e)}"
            return False

    def _generate_videos_with_progress(self, state: VideoGenerationState) -> bool:
        """Generate videos with progress tracking"""
        try:
            scenes = state["architecture"].get("scenes", [])
            if not scenes:
                raise Exception("No scenes in architecture")
            
            video_results = {}
            
            for i, scene in enumerate(scenes):
                scene_progress = 20 + (i / len(scenes)) * 40
                
                if state["progress_callback"]:
                    state["progress_callback"](
                        int(scene_progress),
                        f"Generating scene {i+1}/{len(scenes)}: {scene.get('type', 'unknown')}"
                    )
                
                video_path = self.video_service.generate_scene_video(
                    scene=scene,
                    temp_dir=state["temp_dir"],
                    product_image_url=state["brand_info"].get("product_image_url")
                )
                
                if not video_path:
                    raise Exception(f"Failed to generate scene {i+1}")
                
                video_results[f"scene_{i+1}"] = video_path
            
            state["video_results"] = video_results
            return True
            
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            return False

    def _generate_audio_with_progress(self, state: VideoGenerationState) -> bool:
        """Generate audio with progress tracking"""
        try:
            if state["progress_callback"]:
                state["progress_callback"](25, "Generating voiceover...")
            
            # Extract script from architecture
            script_parts = []
            for scene in state["architecture"].get("scenes", []):
                if scene.get("voiceover"):
                    script_parts.append(scene["voiceover"])
            
            full_script = " ".join(script_parts)
            
            if not full_script.strip():
                raise Exception("No script content for audio generation")
            
            audio_path = self.audio_service.generate_voiceover(
                script=full_script,
                tone=state["brand_info"]["tone"],
                temp_dir=state["temp_dir"]
            )
            
            if not audio_path:
                raise Exception("Failed to generate audio")
            
            state["audio_path"] = audio_path
            return True
            
        except Exception as e:
            logger.error(f"Audio generation failed: {e}")
            return False

    def _execute_assembly_step(self, state: VideoGenerationState) -> Optional[str]:
        """Execute final assembly step"""
        try:
            if state["progress_callback"]:
                state["progress_callback"](85, "Assembling final video...")
            
            # Prepare video clips in order
            video_clips = []
            scenes = state["architecture"].get("scenes", [])
            
            for i, scene in enumerate(scenes):
                scene_key = f"scene_{i+1}"
                if scene_key in state["video_results"]:
                    video_clips.append(state["video_results"][scene_key])
                else:
                    raise Exception(f"Missing video for scene {i+1}")
            
            if not video_clips:
                raise Exception("No video clips to assemble")
            
            # Generate output filename
            timestamp = int(time.time())
            output_filename = f"ad_{timestamp}_{state['generation_id'][:8]}.mp4"
            output_path = Path("outputs") / output_filename
            
            # Ensure outputs directory exists
            output_path.parent.mkdir(exist_ok=True)
            
            if state["progress_callback"]:
                state["progress_callback"](90, "Combining video and audio...")
            
            # Assemble final video
            final_video = self.assembly_service.assemble_final_video(
                video_clips=video_clips,
                audio_path=state["audio_path"],
                output_path=str(output_path),
                target_duration=state["brand_info"]["duration"]
            )
            
            if not final_video or not Path(final_video).exists():
                raise Exception("Final video assembly failed")
            
            # Save final checkpoint
            state["checkpoints"]["assembly"] = {
                "completed": True,
                "timestamp": time.time(),
                "output_path": final_video,
                "file_size": Path(final_video).stat().st_size
            }
            
            if state["progress_callback"]:
                state["progress_callback"](100, "Video generation completed successfully!")
            
            state["success"] = True
            state["output_path"] = final_video
            
            logger.info(f"Video generation completed: {final_video}")
            return final_video
            
        except Exception as e:
            logger.error(f"Assembly step failed: {e}")
            state["error"] = f"Assembly failed: {str(e)}"
            return None

    def _create_cache_key(self, brand_info: Dict[str, Any]) -> str:
        """Create cache key for planning results"""
        import hashlib
        
        # Create hash from key brand info
        key_data = {
            "brand_name": brand_info.get("brand_name", ""),
            "brand_description": brand_info.get("brand_description", ""),
            "product_name": brand_info.get("product_name", ""),
            "target_audience": brand_info.get("target_audience", ""),
            "creative_style": brand_info.get("creative_style", ""),
            "duration": brand_info.get("duration", 18)
        }
        
        key_string = str(sorted(key_data.items()))
        return hashlib.md5(key_string.encode()).hexdigest()

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            "total_generations": self.generation_stats["total_generations"],
            "successful_generations": self.generation_stats["successful_generations"],
            "success_rate": (
                self.generation_stats["successful_generations"] / 
                max(1, self.generation_stats["total_generations"])
            ) * 100,
            "average_duration": self.generation_stats["average_duration"],
            "cache_size": len(self.cache)
        }

    def clear_cache(self):
        """Clear the planning cache"""
        self.cache.clear()
        logger.info("Planning cache cleared")

    def shutdown(self):
        """Shutdown the orchestrator"""
        self.executor.shutdown(wait=True)
        logger.info("Orchestrator shutdown complete")
