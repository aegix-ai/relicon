"""
Script Generation Tool
Creates compelling voiceover scripts with visual cues
"""
import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage

from config.settings import settings, logger


def run(concept_data: str) -> str:
    """
    Generate detailed script segments based on creative concept
    
    Args:
        concept_data: JSON string containing concept information
        
    Returns:
        JSON string with script segments including voiceover and visual hints
    """
    try:
        # Parse concept data
        if isinstance(concept_data, str):
            try:
                concept = json.loads(concept_data)
            except json.JSONDecodeError:
                # Fallback: treat as simple text concept
                concept = {"concept": concept_data, "tone": "professional"}
        else:
            concept = concept_data
            
        logger.info("Generating script", concept_tone=concept.get('tone', 'unknown'))
        
        # Initialize LLM
        llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )
        
        # Create comprehensive script generation prompt
        system_prompt = """You are an elite advertising copywriter with expertise in short-form video scripts. Your specialty is creating compelling narratives that work perfectly for 15-60 second video ads.

SCRIPT WRITING PRINCIPLES:
- Every word must serve a purpose (no filler)
- Create emotional hooks that capture attention immediately
- Build clear narrative arc even in short timeframes
- Integrate brand messaging naturally, never forcefully
- Write for spoken delivery (conversational, not literary)
- Consider visual storytelling alongside voiceover

TECHNICAL REQUIREMENTS:
- 2.5-3 words per second for natural speech pacing
- Each segment should be 2-8 seconds long
- Clear visual direction for each segment
- Smooth transitions between segments
- Strong opening hook and compelling close

OUTPUT FORMAT:
Provide script as structured JSON with detailed segments including precise voiceover text and visual directions."""

        # Calculate target parameters
        estimated_duration = concept.get('estimated_duration', 30)
        target_word_count = int(estimated_duration * 2.5)  # 2.5 words per second
        target_segments = max(3, min(6, estimated_duration // 8))  # 3-6 segments
        
        user_prompt = f"""
CREATIVE CONCEPT:
{json.dumps(concept, indent=2)}

SCRIPT SPECIFICATIONS:
- Target Duration: {estimated_duration} seconds
- Target Word Count: ~{target_word_count} words
- Target Segments: {target_segments} scenes
- Tone: {concept.get('tone', 'professional')}
- Key Messages: {concept.get('key_points', [])}

Create a compelling script that:

1. OPENS WITH POWERFUL HOOK: First 3 seconds must capture attention
2. BUILDS EMOTIONAL CONNECTION: Create genuine viewer engagement
3. COMMUNICATES KEY BENEFITS: Integrate brand value propositions naturally
4. DRIVES TO ACTION: End with compelling call-to-action
5. SUPPORTS VISUAL STORYTELLING: Each segment has clear visual direction

REQUIREMENTS:
- Write in natural, conversational tone for voiceover
- Each segment should be 2-8 seconds when spoken
- Include specific visual hints for stock footage selection
- Consider pacing and emotional flow
- End with brand name and call-to-action
- Total word count should be ~{target_word_count} words

Respond with JSON structure:
{{
  "script_segments": [
    {{
      "scene": 1,
      "voiceover": "Exact text to be spoken",
      "visual_hint": "Detailed description for stock footage search",
      "duration": estimated_seconds,
      "emotional_tone": "tone for this segment",
      "purpose": "what this segment accomplishes"
    }}
  ],
  "total_estimated_duration": seconds,
  "total_word_count": count,
  "script_summary": "overall narrative description",
  "call_to_action": "final CTA text"
}}
"""

        # Generate script
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            SystemMessage(content=user_prompt)
        ])
        
        # Parse and validate response
        try:
            script_data = json.loads(response.content)
            
            # Validate and enhance script structure
            script_segments = script_data.get('script_segments', [])
            
            if not script_segments:
                # Create fallback script structure
                script_segments = _create_fallback_script(concept, estimated_duration)
                script_data['script_segments'] = script_segments
            
            # Ensure all segments have required fields
            for i, segment in enumerate(script_segments):
                if 'scene' not in segment:
                    segment['scene'] = i + 1
                if 'duration' not in segment:
                    word_count = len(segment.get('voiceover', '').split())
                    segment['duration'] = max(2.0, word_count / 2.5)
                if 'visual_hint' not in segment:
                    segment['visual_hint'] = f"Visual for scene {i + 1}"
                if 'emotional_tone' not in segment:
                    segment['emotional_tone'] = concept.get('tone', 'professional')
            
            # Calculate actual totals
            script_data['total_estimated_duration'] = sum(seg.get('duration', 0) for seg in script_segments)
            script_data['total_word_count'] = sum(len(seg.get('voiceover', '').split()) for seg in script_segments)
            
            # Add metadata
            script_data['generated_by'] = 'ReelForge Script Generator'
            script_data['version'] = '1.0'
            script_data['concept_alignment'] = _analyze_concept_alignment(script_segments, concept)
            
            logger.info("Script generated successfully",
                       segments=len(script_segments),
                       duration=script_data['total_estimated_duration'],
                       words=script_data['total_word_count'])
            
            return json.dumps(script_data, indent=2)
            
        except json.JSONDecodeError:
            # Create fallback script from text response
            logger.warning("JSON parsing failed, creating fallback script")
            fallback_script = _create_fallback_script_from_text(response.content, concept, estimated_duration)
            return json.dumps(fallback_script, indent=2)
            
    except Exception as e:
        error_msg = f"Script generation failed: {str(e)}"
        logger.error("Script generation error", error=str(e))
        
        # Return error in expected format
        error_response = {
            "error": error_msg,
            "script_segments": [],
            "total_estimated_duration": 0,
            "generated_by": "ReelForge Script Generator (Error)"
        }
        
        return json.dumps(error_response, indent=2)


def _create_fallback_script(concept: Dict[str, Any], duration: int) -> List[Dict[str, Any]]:
    """Create a basic fallback script structure"""
    brand_name = concept.get('brand_name', 'Our Product')
    tone = concept.get('tone', 'professional')
    
    return [
        {
            "scene": 1,
            "voiceover": f"Discover {brand_name} - the solution you've been waiting for.",
            "visual_hint": "Product introduction or brand logo reveal",
            "duration": duration * 0.3,
            "emotional_tone": "engaging",
            "purpose": "hook and introduction"
        },
        {
            "scene": 2,
            "voiceover": "Experience the difference with our innovative approach.",
            "visual_hint": "Product in use or benefits demonstration",
            "duration": duration * 0.4,
            "emotional_tone": tone,
            "purpose": "benefit communication"
        },
        {
            "scene": 3,
            "voiceover": f"Join thousands who trust {brand_name}. Try it today!",
            "visual_hint": "Happy customers or call-to-action visual",
            "duration": duration * 0.3,
            "emotional_tone": "compelling",
            "purpose": "call-to-action"
        }
    ]


def _create_fallback_script_from_text(text_response: str, concept: Dict[str, Any], duration: int) -> Dict[str, Any]:
    """Create script structure from unparsed text response"""
    # Split text into rough segments
    sentences = [s.strip() for s in text_response.split('.') if s.strip()]
    
    # Take first few sentences as script segments
    segments = []
    for i, sentence in enumerate(sentences[:4]):  # Max 4 segments
        if sentence:
            segments.append({
                "scene": i + 1,
                "voiceover": sentence + ".",
                "visual_hint": f"Visual supporting: {sentence[:50]}...",
                "duration": max(2.0, len(sentence.split()) / 2.5),
                "emotional_tone": concept.get('tone', 'professional'),
                "purpose": "script segment"
            })
    
    return {
        "script_segments": segments,
        "total_estimated_duration": sum(seg['duration'] for seg in segments),
        "total_word_count": sum(len(seg['voiceover'].split()) for seg in segments),
        "script_summary": "Fallback script generated from text response",
        "generated_by": "ReelForge Script Generator (Fallback)",
        "note": "Generated from unparsed LLM response"
    }


def _analyze_concept_alignment(script_segments: List[Dict[str, Any]], concept: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze how well the script aligns with the original concept"""
    concept_keywords = set()
    
    # Extract keywords from concept
    for key in ['concept', 'hook', 'key_points']:
        if key in concept:
            value = concept[key]
            if isinstance(value, str):
                concept_keywords.update(value.lower().split())
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        concept_keywords.update(item.lower().split())
    
    # Analyze script content
    script_text = ' '.join(seg.get('voiceover', '') for seg in script_segments).lower()
    script_words = set(script_text.split())
    
    # Calculate alignment metrics
    keyword_overlap = len(concept_keywords.intersection(script_words))
    alignment_score = keyword_overlap / len(concept_keywords) if concept_keywords else 0
    
    return {
        "alignment_score": alignment_score,
        "keyword_overlap": keyword_overlap,
        "concept_keywords_found": list(concept_keywords.intersection(script_words)),
        "tone_consistency": concept.get('tone', 'unknown') in script_text
    }
