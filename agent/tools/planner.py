"""
Timeline Planning Tool
Bridges script segments to detailed FFmpeg-ready timeline
"""
import json
from typing import Dict, Any, List
from agent.planning import create_comprehensive_plan, validate_timeline
from config.settings import settings, logger


def run(script_data: str) -> str:
    """
    Create detailed execution timeline from script segments
    
    This is the critical bridge between high-level planning and technical execution.
    Converts script segments into precise timeline with timing, transitions, and assembly logic.
    
    Args:
        script_data: JSON string containing script segments and concept information
        
    Returns:
        JSON string with detailed timeline ready for FFmpeg compilation
    """
    try:
        # Parse script data
        if isinstance(script_data, str):
            try:
                script_info = json.loads(script_data)
            except json.JSONDecodeError:
                logger.error("Invalid JSON in script data")
                raise ValueError("Script data must be valid JSON")
        else:
            script_info = script_data
            
        script_segments = script_info.get('script_segments', [])
        if not script_segments:
            raise ValueError("No script segments found in input data")
            
        logger.info("Creating timeline plan", segments=len(script_segments))
        
        # Extract concept information if available
        concept_info = script_info.get('concept', {})
        if isinstance(concept_info, str):
            try:
                concept_info = json.loads(concept_info)
            except json.JSONDecodeError:
                concept_info = {"tone": "professional"}
        
        # Create comprehensive execution plan
        timeline_plan = create_comprehensive_plan(concept_info, script_segments)
        
        # Validate the timeline
        validation_results = validate_timeline(timeline_plan['timeline'])
        
        if not validation_results['valid']:
            logger.error("Timeline validation failed", errors=validation_results['errors'])
            # Try to fix common issues
            timeline_plan = _fix_timeline_issues(timeline_plan, validation_results)
            
            # Re-validate
            validation_results = validate_timeline(timeline_plan['timeline'])
            if not validation_results['valid']:
                raise ValueError(f"Timeline validation failed: {validation_results['errors']}")
        
        # Add planning metadata
        planning_metadata = {
            "planner_version": "1.0",
            "generated_by": "ReelForge Timeline Planner",
            "validation_results": validation_results,
            "planning_strategy": _determine_planning_strategy(script_segments, concept_info),
            "execution_notes": _generate_execution_notes(timeline_plan)
        }
        
        timeline_plan['metadata'] = planning_metadata
        
        logger.info("Timeline plan created successfully",
                   timeline_items=len(timeline_plan['timeline']),
                   total_duration=timeline_plan['total_duration'],
                   validation_status=validation_results['valid'])
        
        return json.dumps(timeline_plan, indent=2)
        
    except Exception as e:
        error_msg = f"Timeline planning failed: {str(e)}"
        logger.error("Timeline planning error", error=str(e))
        
        # Return error in expected format
        error_response = {
            "error": error_msg,
            "timeline": [],
            "total_duration": 0,
            "audio_plan": {},
            "generated_by": "ReelForge Timeline Planner (Error)"
        }
        
        return json.dumps(error_response, indent=2)


def _fix_timeline_issues(timeline_plan: Dict[str, Any], validation_results: Dict[str, Any]) -> Dict[str, Any]:
    """Attempt to fix common timeline validation issues"""
    timeline = timeline_plan['timeline']
    errors = validation_results.get('errors', [])
    
    # Fix duration issues
    for error in errors:
        if "exceeds maximum" in error:
            # Proportionally reduce all segment durations
            total_duration = sum(item.get('duration', 0) for item in timeline)
            reduction_factor = settings.max_video_duration / total_duration * 0.95  # 5% buffer
            
            for item in timeline:
                if 'duration' in item:
                    item['duration'] *= reduction_factor
            
            # Recalculate total duration
            timeline_plan['total_duration'] = sum(item.get('duration', 0) for item in timeline)
            
            logger.info("Reduced timeline duration", 
                       reduction_factor=reduction_factor,
                       new_duration=timeline_plan['total_duration'])
    
    # Add missing logo segment
    if any("Logo end segment is required" in error for error in errors):
        logo_segment = {
            "type": "logo_end",
            "start_time": timeline_plan['total_duration'],
            "duration": 2.0,
            "properties": {
                "call_to_action": True,
                "fade_in": True
            }
        }
        timeline.append(logo_segment)
        timeline_plan['total_duration'] += 2.0
        
        logger.info("Added missing logo segment")
    
    return timeline_plan


def _determine_planning_strategy(script_segments: List[Dict[str, Any]], concept_info: Dict[str, Any]) -> Dict[str, Any]:
    """Determine the optimal planning strategy based on content analysis"""
    
    # Analyze script characteristics
    total_segments = len(script_segments)
    avg_segment_duration = sum(seg.get('duration', 0) for seg in script_segments) / total_segments if total_segments > 0 else 0
    energy_levels = [seg.get('emotional_tone', 'medium') for seg in script_segments]
    
    # Determine pacing strategy
    if avg_segment_duration < 3:
        pacing_strategy = "fast_cuts"
    elif avg_segment_duration > 6:
        pacing_strategy = "slow_build"
    else:
        pacing_strategy = "balanced"
    
    # Determine transition strategy
    high_energy_count = sum(1 for tone in energy_levels if tone in ['high', 'energetic', 'exciting'])
    if high_energy_count > len(energy_levels) * 0.6:
        transition_strategy = "dynamic"
    else:
        transition_strategy = "smooth"
    
    # Determine visual strategy
    visual_hints = [seg.get('visual_hint', '') for seg in script_segments]
    product_focus_count = sum(1 for hint in visual_hints if any(word in hint.lower() for word in ['product', 'brand', 'logo']))
    
    if product_focus_count > len(visual_hints) * 0.5:
        visual_strategy = "product_focused"
    else:
        visual_strategy = "lifestyle_focused"
    
    return {
        "pacing_strategy": pacing_strategy,
        "transition_strategy": transition_strategy,
        "visual_strategy": visual_strategy,
        "complexity_level": "high" if total_segments > 5 else "standard",
        "brand_integration": concept_info.get('tone', 'professional')
    }


def _generate_execution_notes(timeline_plan: Dict[str, Any]) -> List[str]:
    """Generate specific notes for FFmpeg execution"""
    notes = []
    
    timeline = timeline_plan.get('timeline', [])
    total_duration = timeline_plan.get('total_duration', 0)
    
    # Duration notes
    if total_duration > 45:
        notes.append("Long-form content: ensure pacing maintains engagement")
    elif total_duration < 20:
        notes.append("Short-form content: maximize impact per second")
    
    # Transition notes
    transition_count = sum(1 for item in timeline if item.get('type') == 'transition')
    if transition_count > 5:
        notes.append("High transition count: ensure smooth flow and consistent timing")
    
    # Audio notes
    audio_plan = timeline_plan.get('audio_plan', {})
    if audio_plan.get('background_music', {}).get('enabled'):
        notes.append("Background music enabled: balance levels for clear voiceover")
    
    # Quality notes
    video_segments = [item for item in timeline if item.get('type') == 'video']
    if len(video_segments) > 6:
        notes.append("Multiple video segments: ensure consistent visual quality and style")
    
    # Brand safety notes
    if any(item.get('type') == 'logo_end' for item in timeline):
        notes.append("Logo end segment included: ensure prominent brand presentation")
    
    return notes


def create_ffmpeg_preparation_data(timeline_plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare data specifically formatted for FFmpeg compilation
    This creates the bridge between timeline planning and FFmpeg execution
    """
    timeline = timeline_plan.get('timeline', [])
    audio_plan = timeline_plan.get('audio_plan', {})
    
    # Separate timeline items by type
    video_segments = [item for item in timeline if item.get('type') == 'video']
    transitions = [item for item in timeline if item.get('type') == 'transition']
    audio_segments = audio_plan.get('voiceover_track', {}).get('segments', [])
    
    # Create input file list (will be populated during execution)
    input_files = {
        "video_files": [f"video_{i}.mp4" for i in range(len(video_segments))],
        "audio_files": [f"audio_{i}.wav" for i in range(len(audio_segments))],
        "background_music": "background.mp3" if audio_plan.get('background_music', {}).get('enabled') else None
    }
    
    # Create filter complex preparation
    filter_preparation = {
        "video_inputs": len(video_segments),
        "audio_inputs": len(audio_segments),
        "has_background_music": bool(audio_plan.get('background_music', {}).get('enabled')),
        "transition_count": len(transitions),
        "total_duration": timeline_plan.get('total_duration', 0)
    }
    
    return {
        "input_files": input_files,
        "filter_preparation": filter_preparation,
        "timeline_structure": timeline,
        "audio_structure": audio_plan,
        "execution_ready": True
    }
