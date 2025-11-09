# type: ignore

# 1st

"""
  Main video generation pipeline using LangGraph state machine.
  Simple, direct orchestration: plan → generate videos → generate audio → assemble.
"""

import os
import time
import tempfile
from typing import Dict, Any, Optional, TypedDict, Annotated
from pathlib import Path
from langgraph.graph import StateGraph
from core.video_planner import PlanningService
from core.video_generator import VideoService
from core.audio_orchestrator import AudioService
from core.video_assembler import AssemblyService
from core.cost_tracker import cost_tracker
from core.logger import get_logger

logger = get_logger("pipeline")


class PipelineState(TypedDict):
    """State for video generation pipeline"""
    # Input
    brand_info: Dict[str, Any]

    # Pipeline data
    architecture: Optional[Dict[str, Any]]
    video_paths: list[str]
    audio_path: Optional[str]
    output_path: Optional[str]

    # Metadata
    temp_dir: str
    generation_id: str
    error: Optional[str]


class VideoGenerationPipeline:
    """
    Core video generation pipeline.
    Handles: angle → scenes → video generation → audio → assembly
    """

    def __init__(self):
        self.planner = PlanningService()
        self.video_service = VideoService()
        self.audio_service = AudioService()
        self.assembler = AssemblyService()

        # Build LangGraph workflow
        self.workflow = self._build_workflow()

        logger.info("Pipeline initialized")

    def _build_workflow(self) -> StateGraph:
        """Build LangGraph state machine for pipeline"""
        graph = StateGraph(PipelineState)

        # Add pipeline nodes
        graph.add_node("plan", self._plan_video)
        graph.add_node("generate_videos", self._generate_videos)
        graph.add_node("generate_audio", self._generate_audio)
        graph.add_node("assemble", self._assemble_final_video)

        # Define flow
        graph.set_entry_point("plan")
        graph.add_edge("plan", "generate_videos")
        graph.add_edge("generate_videos", "generate_audio")
        graph.add_edge("generate_audio", "assemble")
        # "assemble" node has no outgoing edges, so it's automatically an end node

        return graph.compile()

    def _plan_video(self, state: PipelineState) -> PipelineState:
        """Step 1: Plan video architecture (angle → scenes)"""
        try:
            logger.info("Planning video architecture", "pipeline.plan.start")

            architecture = self.planner.create_video_architecture(
                brand_info=state["brand_info"]
            )

            if not architecture:
                raise Exception("Failed to create video architecture")

            state["architecture"] = architecture
            logger.info("Video architecture created", "pipeline.plan.complete",
                       scene_count=len(architecture.get("scene_architecture", {}).get("scenes", [])))

        except Exception as e:
            logger.error(f"Planning failed: {e}", "pipeline.plan.error")
            state["error"] = str(e)

        return state

    def _generate_videos(self, state: PipelineState) -> PipelineState:
        """Step 2: Generate video scenes (with caching)"""
        try:
            if state.get("error"):
                return state

            logger.info("Generating video scenes", "pipeline.video.start")

            architecture = state["architecture"]
            scenes = architecture.get("scene_architecture", {}).get("scenes", [])

            if not scenes:
                raise Exception("No scenes in architecture")

            video_paths = []
            temp_dir = state["temp_dir"]
            product_image_url = state["brand_info"].get("product_image_url")

            for i, scene in enumerate(scenes):
                logger.info(f"Generating scene {i+1}/{len(scenes)}", "pipeline.video.scene")

                video_path = self.video_service.generate_scene_video(
                    scene=scene,
                    temp_dir=temp_dir,
                    product_image_url=product_image_url
                )

                if not video_path:
                    raise Exception(f"Failed to generate scene {i+1}")

                video_paths.append(video_path)

            state["video_paths"] = video_paths
            logger.info("All video scenes generated", "pipeline.video.complete",
                       scene_count=len(video_paths))

        except Exception as e:
            logger.error(f"Video generation failed: {e}", "pipeline.video.error")
            state["error"] = str(e)

        return state

    def _generate_audio(self, state: PipelineState) -> PipelineState:
        """Step 3: Generate voiceover + music"""
        try:
            if state.get("error"):
                return state

            logger.info("Generating audio track", "pipeline.audio.start")

            audio_path = os.path.join(state["temp_dir"], "audio_complete.mp3")

            success = self.audio_service.generate_audio_from_architecture(
                architecture=state["architecture"],
                output_path=audio_path
            )

            if not success or not os.path.exists(audio_path):
                raise Exception("Failed to generate audio")

            state["audio_path"] = audio_path
            logger.info("Audio track generated", "pipeline.audio.complete")

        except Exception as e:
            logger.error(f"Audio generation failed: {e}", "pipeline.audio.error")
            state["error"] = str(e)

        return state

    def _assemble_final_video(self, state: PipelineState) -> PipelineState:
        """Step 4: Assemble final video with FFmpeg"""
        try:
            if state.get("error"):
                return state

            logger.info("Assembling final video", "pipeline.assembly.start")

            # Create output path
            timestamp = int(time.time())
            output_filename = f"ad_{timestamp}_{state['generation_id'][:8]}.mp4"
            output_path = Path("outputs") / output_filename
            output_path.parent.mkdir(exist_ok=True)

            # Assemble
            success = self.assembler.assemble_final_video(
                video_files=state["video_paths"],
                audio_file=state["audio_path"],
                output_path=str(output_path),
                target_duration=state["brand_info"].get("duration", 15)
            )

            if not success:
                raise Exception("Video assembly failed")

            state["output_path"] = str(output_path)
            logger.info(f"Final video assembled: {output_path}", "pipeline.assembly.complete")

        except Exception as e:
            logger.error(f"Assembly failed: {e}", "pipeline.assembly.error")
            state["error"] = str(e)

        return state

    def generate(self, brand_info: Dict[str, Any]) -> Optional[str]:
        """
        Generate complete video ad from brand information.

        Args:
            brand_info: Dict with brand_name, brand_description, product_name, etc.

        Returns:
            Path to generated video file or None if failed
        """
        import uuid

        generation_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        try:
            logger.info("Starting video generation", "pipeline.start",
                       generation_id=generation_id)

            # Create temp directory
            with tempfile.TemporaryDirectory(prefix="relicon_") as temp_dir:

                # Initialize state
                state: PipelineState = {
                    "brand_info": brand_info,
                    "architecture": None,
                    "video_paths": [],
                    "audio_path": None,
                    "output_path": None,
                    "temp_dir": temp_dir,
                    "generation_id": generation_id,
                    "error": None
                }

                # Run pipeline
                result = self.workflow.invoke(state)

                # Check result
                if result.get("error"):
                    logger.error(f"Pipeline failed: {result['error']}", "pipeline.failed")
                    return None

                output_path = result.get("output_path")
                if not output_path:
                    logger.error("No output path in result", "pipeline.failed")
                    return None

                duration = time.time() - start_time

                # Log cost
                cost_estimate = cost_tracker.estimate_video_cost(
                    scene_count=len(result.get("video_paths", [])),
                    resolution=brand_info.get("resolution", "720p"),
                    duration=brand_info.get("duration", 15)
                )

                logger.info(
                    f"Video generation complete in {duration:.2f}s",
                    "pipeline.complete",
                    generation_id=generation_id,
                    output_path=output_path,
                    cost=cost_estimate.total_estimated_cost
                )

                return output_path

        except Exception as e:
            logger.error(f"Pipeline error: {e}", "pipeline.error",
                        generation_id=generation_id)
            return None


# Global pipeline instance
pipeline = VideoGenerationPipeline()
