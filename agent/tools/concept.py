"""
Concept Generation Tool
Creates innovative creative concepts and hooks for video ads
"""
import json
import os
from typing import Dict, Any
from openai import OpenAI

class ConceptGenerationTool:
    """
    AI-powered concept generation tool that creates compelling video ad concepts
    """
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def run(self, input_data: str) -> str:
        """
        Generate creative concept and hook for video ad
        
        Args:
            input_data: JSON string containing brand information
            
        Returns:
            JSON string with detailed concept information
        """
        try:
            # Parse input data
            brand_info = json.loads(input_data)
            
            # Create concept generation prompt
            prompt = f"""
            Create a REVOLUTIONARY concept for a {brand_info.get('duration', 30)}-second SHORT-FORM video ad that will STOP SCROLLERS in their tracks.
            
            BRAND CONTEXT:
            - Brand: {brand_info.get('brand_name', 'Unknown Brand')}
            - Description: {brand_info.get('brand_description', 'No description')}
            - Target: {brand_info.get('target_audience', 'General audience')}
            - Tone: {brand_info.get('tone', 'professional')}
            - CTA: {brand_info.get('call_to_action', 'Learn more')}
            
            SHORT-FORM VIDEO REQUIREMENTS:
            1. THUMB-STOPPING POWER - Must captivate within 1-2 seconds
            2. SCROLL-WORTHY CONCEPT - Unique enough to share and save
            3. EMOTIONAL TRIGGER - Instant connection with target audience
            4. VISUAL MAGNETISM - Compelling visual storytelling
            5. ACTION-DRIVEN - Clear path to conversion
            
            CREATIVE INNOVATION FACTORS:
            - Use unexpected angles or surprising reveals
            - Leverage current trends and cultural moments
            - Create "aha moments" that viewers remember
            - Design for multiple viewings and shareability
            - Optimize for vertical mobile viewing
            
            OUTPUT JSON FORMAT:
            {{
                "concept": "Revolutionary 2-3 sentence concept description",
                "hook": "Irresistible opening hook (under 10 words)",
                "visual_style": "Specific visual direction for dynamic short-form content",
                "key_message": "Core benefit that drives action",
                "emotional_appeal": "Primary emotion (curiosity/urgency/excitement/trust)",
                "uniqueness_factor": "What makes this concept thumb-stopping",
                "engagement_strategy": "How this will drive saves, shares, and comments",
                "trend_alignment": "Current trends this concept leverages",
                "mobile_optimization": "Vertical video considerations"
            }}
            
            Make this concept so compelling that viewers HAVE to watch it through to the end!
            """
            
            # Generate concept using GPT-4o
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": "You are a world-class creative director specializing in viral video ads. Create revolutionary concepts that break through the noise."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.8
            )
            
            concept_result = response.choices[0].message.content
            
            # Parse and validate the response
            concept_data = json.loads(concept_result)
            
            # Add metadata
            concept_data.update({
                "brand_name": brand_info.get('brand_name'),
                "generated_at": "2024-06-29T08:52:00Z",
                "tool": "concept_generation",
                "status": "success"
            })
            
            return json.dumps(concept_data)
            
        except Exception as e:
            return json.dumps({
                "error": f"Concept generation failed: {str(e)}",
                "status": "failed",
                "tool": "concept_generation"
            })

def analyze_trends(keywords: list) -> Dict[str, Any]:
    """
    Analyze current trends relevant to given keywords
    This is a helper function for more sophisticated trend integration
    """
    # In a real implementation, this would connect to trend APIs
    # For now, return mock trend data
    return {
        "trending_topics": ["sustainability", "innovation", "authenticity"],
        "visual_trends": ["minimalist", "bold_colors", "natural_lighting"],
        "audio_trends": ["upbeat", "conversational", "ambient"]
    }