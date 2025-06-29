"""
Advanced planning algorithms for video generation
Converts high-level concepts into detailed execution timelines
"""
from typing import Dict, List, Any
import json
from config.settings import settings, logger


def create_comprehensive_plan(concept: Dict[str, Any], script_segments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create exhaustive execution plan from concept and script
    
    This function bridges the gap between creative planning and technical execution
    by creating detailed timelines with precise timing and assembly instructions.
    """
    
    try:
        total_duration = sum(seg.get('duration', 0) for seg in script_segments)
        if total_duration == 0:
            # Estimate durations if not provided
            words_per_second = 2.5
            for seg in script_segments:
                word_count = len(seg['voiceover'].split())
                seg['duration'] = max(2.0, word_count / words_per_second)
            total_duration = sum(seg['duration'] for seg in script_segments)
        
        # Create detailed timeline
        timeline = []
        current_time = 0
        
        for i, segment in enumerate(script_segments):
            duration = segment['duration']
            
            # Add main video segment
            timeline.append({
                "type": "video",
                "scene_id": segment['scene'],
                "start_time": current_time,
                "duration": duration,
                "search_query": segment['visual_hint'],
                "voiceover_text": segment['voiceover'],
                "properties": {
                    "scene_type": _classify_scene_type(segment['visual_hint']),
                    "energy_level": _analyze_energy_level(segment['voiceover'])
                }
            })
            
            current_time += duration
            
            # Add transition (except for last segment)
            if i < len(script_segments) - 1:
                transition_type = _select_optimal_transition(
                    segment['visual_hint'], 
                    script_segments[i + 1]['visual_hint']
                )
                transition_duration = _calculate_transition_duration(transition_type)
                
                timeline.append({
                    "type": "transition",
                    "name": transition_type,
                    "start_time": current_time,
                    "duration": transition_duration,
                    "properties": {
                        "from_scene": segment['scene'],
                        "to_scene": script_segments[i + 1]['scene']
                    }
                })
                
                current_time += transition_duration
        
        # Add logo end segment (mandatory)
        if settings.require_logo_end:
            logo_duration = 2.0
            timeline.append({
                "type": "logo_end",
                "start_time": current_time,
                "duration": logo_duration,
                "properties": {
                    "call_to_action": True,
                    "fade_in": True
                }
            })
            current_time += logo_duration
        
        # Create audio mixing plan
        audio_plan = _create_audio_mixing_plan(script_segments, total_duration)
        
        # Create final assembly instructions
        assembly_instructions = {
            "timeline": timeline,
            "audio_plan": audio_plan,
            "total_duration": current_time,
            "quality_settings": {
                "resolution": "1920x1080",
                "framerate": 30,
                "bitrate": "5M",
                "codec": "h264"
            },
            "validation_rules": {
                "max_duration": settings.max_video_duration,
                "require_logo": settings.require_logo_end,
                "min_scene_duration": settings.min_scene_duration
            }
        }
        
        logger.info("Comprehensive plan created", 
                   timeline_items=len(timeline),
                   total_duration=current_time)
        
        return assembly_instructions
        
    except Exception as e:
        logger.error("Planning failed", error=str(e))
        raise


def _classify_scene_type(visual_hint: str) -> str:
    """Classify scene type based on visual description"""
    hint_lower = visual_hint.lower()
    
    if any(word in hint_lower for word in ['product', 'bottle', 'package', 'logo']):
        return 'product_focus'
    elif any(word in hint_lower for word in ['person', 'people', 'customer', 'user']):
        return 'human_focus'
    elif any(word in hint_lower for word in ['action', 'movement', 'exercise', 'activity']):
        return 'action'
    elif any(word in hint_lower for word in ['lifestyle', 'environment', 'setting', 'background']):
        return 'lifestyle'
    else:
        return 'generic'


def _analyze_energy_level(voiceover_text: str) -> str:
    """Analyze energy level of voiceover text"""
    text_lower = voiceover_text.lower()
    
    # High energy indicators
    high_energy_words = ['amazing', 'incredible', 'breakthrough', 'revolutionary', 'wow', '!']
    high_energy_count = sum(1 for word in high_energy_words if word in text_lower)
    
    if high_energy_count >= 2 or text_lower.count('!') >= 2:
        return 'high'
    elif any(word in text_lower for word in ['calm', 'peaceful', 'gentle', 'smooth']):
        return 'low'
    else:
        return 'medium'


def _select_optimal_transition(from_hint: str, to_hint: str) -> str:
    """Intelligently select transition based on scene context"""
    from_type = _classify_scene_type(from_hint)
    to_type = _classify_scene_type(to_hint)
    
    # Transition logic based on scene types
    if from_type == 'product_focus' and to_type == 'human_focus':
        return 'dissolve'
    elif from_type == 'human_focus' and to_type == 'action':
        return 'wipe'
    elif from_type == 'action' and to_type == 'product_focus':
        return 'zoom'
    elif from_type == to_type:
        return 'crossfade'
    else:
        # Use available transitions from settings
        transitions = settings.available_transitions
        # Simple selection logic - can be made more sophisticated
        return transitions[hash(from_hint + to_hint) % len(transitions)]


def _calculate_transition_duration(transition_type: str) -> float:
    """Calculate optimal transition duration"""
    transition_durations = {
        'fade': 0.5,
        'crossfade': 0.8,
        'dissolve': 0.6,
        'wipe': 0.4,
        'slide': 0.3,
        'zoom': 0.7,
        'rotate': 0.5
    }
    return transition_durations.get(transition_type, 0.5)


def _create_audio_mixing_plan(script_segments: List[Dict[str, Any]], total_duration: float) -> Dict[str, Any]:
    """Create detailed audio mixing plan"""
    return {
        "voiceover_track": {
            "segments": [
                {
                    "text": seg['voiceover'],
                    "start_time": sum(s.get('duration', 0) for s in script_segments[:i]),
                    "duration": seg.get('duration', 0)
                }
                for i, seg in enumerate(script_segments)
            ]
        },
        "background_music": {
            "enabled": True,
            "fade_in_duration": 1.0,
            "fade_out_duration": 2.0,
            "volume_level": 0.3,  # 30% volume to not overpower voiceover
            "style": "corporate_upbeat"
        },
        "mixing_settings": {
            "voiceover_volume": 1.0,
            "background_volume": 0.3,
            "audio_normalization": True,
            "compression": True
        }
    }


def validate_timeline(timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate timeline meets all requirements"""
    validation_results = {
        "valid": True,
        "warnings": [],
        "errors": []
    }
    
    total_duration = sum(item.get('duration', 0) for item in timeline)
    
    # Check duration limits
    if total_duration > settings.max_video_duration:
        validation_results["errors"].append(f"Total duration {total_duration}s exceeds maximum {settings.max_video_duration}s")
        validation_results["valid"] = False
    
    # Check for required logo end
    if settings.require_logo_end:
        has_logo = any(item.get('type') == 'logo_end' for item in timeline)
        if not has_logo:
            validation_results["errors"].append("Logo end segment is required but missing")
            validation_results["valid"] = False
    
    # Check for duplicate transitions
    transitions = [item for item in timeline if item.get('type') == 'transition']
    transition_names = [t.get('name') for t in transitions]
    if len(transition_names) != len(set(transition_names)):
        validation_results["warnings"].append("Duplicate transitions detected")
    
    # Check minimum scene durations
    video_segments = [item for item in timeline if item.get('type') == 'video']
    for seg in video_segments:
        if seg.get('duration', 0) < settings.min_scene_duration:
            validation_results["warnings"].append(f"Scene {seg.get('scene_id')} duration below recommended minimum")
    
    return validation_results
