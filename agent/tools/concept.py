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
            Create an innovative, compelling concept for a {brand_info.get('duration', 30)}-second video ad.
            
            Brand Information:
            - Name: {brand_info.get('brand_name', 'Unknown Brand')}
            - Description: {brand_info.get('brand_description', 'No description')}
            - Target Audience: {brand_info.get('target_audience', 'General audience')}
            - Tone: {brand_info.get('tone', 'professional')}
            - Call to Action: {brand_info.get('call_to_action', 'Learn more')}
            
            Requirements:
            1. Create a REVOLUTIONARY concept that stands out from typical ads
            2. Design a powerful hook that grabs attention within 3 seconds
            3. Ensure the concept is perfectly tailored to the target audience
            4. Make it memorable and shareable
            5. Include specific visual style recommendations
            
            Respond with a JSON object containing:
            - concept: The main creative concept (2-3 sentences)
            - hook: The opening hook (1 sentence, maximum impact)
            - visual_style: Detailed visual style guide
            - key_message: Core message to communicate
            - emotional_appeal: Primary emotion to evoke
            - uniqueness_factor: What makes this concept revolutionary
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