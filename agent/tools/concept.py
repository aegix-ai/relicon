"""
Concept Generation Tool
Creates innovative creative concepts and hooks for video ads
"""
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage

from config.settings import settings, logger


def run(input_data: str) -> str:
    """
    Generate creative concept and hook for video ad
    
    Args:
        input_data: JSON string containing brand information
        
    Returns:
        JSON string with detailed concept information
    """
    try:
        # Parse input
        if isinstance(input_data, str):
            try:
                brand_info = json.loads(input_data)
            except json.JSONDecodeError:
                # If not JSON, treat as simple brand description
                brand_info = {"description": input_data}
        else:
            brand_info = input_data
            
        logger.info("Generating concept", brand=brand_info.get('brand_name', 'Unknown'))
        
        # Initialize LLM
        llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )
        
        # Create comprehensive concept generation prompt
        system_prompt = """You are a world-class creative director specializing in breakthrough advertising concepts. Your expertise lies in creating revolutionary ideas that break conventional patterns while maintaining commercial effectiveness.

CORE CREATIVE PRINCIPLES:
- Every concept must be architecturally unique and non-formulaic
- Focus on emotional resonance and psychological impact
- Leverage current cultural trends and social dynamics
- Create concepts that competitors cannot easily replicate
- Balance creativity with commercial viability

CONCEPT FRAMEWORK:
1. HOOK: The magnetic opening that captures immediate attention
2. CORE CONCEPT: The central creative idea that drives the entire ad
3. VISUAL STYLE: Distinctive aesthetic approach and production style
4. EMOTIONAL JOURNEY: How the viewer's emotions evolve throughout
5. BRAND INTEGRATION: How the brand naturally fits into the concept
6. CALL-TO-ACTION STRATEGY: Compelling way to drive viewer action

Respond with a detailed JSON structure containing comprehensive concept development."""

        user_prompt = f"""
BRAND BRIEF:
{json.dumps(brand_info, indent=2)}

Create a revolutionary creative concept for this brand that:

1. BREAKS CONVENTIONAL PATTERNS: Avoid typical ad formulas
2. MAXIMIZES EMOTIONAL IMPACT: Create genuine viewer connection  
3. LEVERAGES CULTURAL RELEVANCE: Tap into current trends/moments
4. ENSURES BRAND MEMORABILITY: Make the brand unforgettable
5. DRIVES COMMERCIAL ACTION: Compel viewers to act

Requirements:
- Must work for short-form video (15-60 seconds)
- Should feel fresh and innovative
- Must align with brand values and target audience
- Include detailed rationale for all creative choices

Provide comprehensive concept development in JSON format with these fields:
- concept: Core creative idea (detailed description)
- hook: Opening strategy to capture attention
- tone: Overall emotional tone and style
- key_points: Essential messages to communicate
- visual_style: Detailed visual approach and aesthetic
- emotional_journey: How viewer emotions evolve
- cultural_context: Relevant trends or cultural moments
- differentiation: What makes this concept unique
- execution_notes: Specific production considerations
- estimated_duration: Recommended video length
"""

        # Generate concept
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            SystemMessage(content=user_prompt)
        ])
        
        # Parse and validate response
        try:
            concept_data = json.loads(response.content)
            
            # Ensure all required fields exist
            required_fields = ['concept', 'hook', 'tone', 'key_points', 'visual_style']
            for field in required_fields:
                if field not in concept_data:
                    concept_data[field] = f"Generated {field} content"
            
            # Add metadata
            concept_data['generated_by'] = 'ReelForge Concept Generator'
            concept_data['version'] = '1.0'
            
            logger.info("Concept generated successfully", 
                       concept_type=concept_data.get('tone', 'unknown'))
            
            return json.dumps(concept_data, indent=2)
            
        except json.JSONDecodeError:
            # Fallback: create structured response from text
            fallback_concept = {
                "concept": response.content[:500],
                "hook": "Compelling opening to capture attention",
                "tone": "professional",
                "key_points": ["Brand awareness", "Product benefits", "Call to action"],
                "visual_style": "Modern and engaging",
                "emotional_journey": "Interest → Desire → Action",
                "estimated_duration": 30,
                "generated_by": "ReelForge Concept Generator (Fallback)",
                "note": "Generated from text response due to JSON parsing issue"
            }
            
            logger.warning("Used fallback concept structure")
            return json.dumps(fallback_concept, indent=2)
            
    except Exception as e:
        error_msg = f"Concept generation failed: {str(e)}"
        logger.error("Concept generation error", error=str(e))
        
        # Return error in expected format
        error_response = {
            "error": error_msg,
            "concept": "Error in concept generation",
            "hook": "Unable to generate hook",
            "tone": "neutral",
            "key_points": ["Error occurred"],
            "visual_style": "Default style",
            "generated_by": "ReelForge Concept Generator (Error)"
        }
        
        return json.dumps(error_response, indent=2)


def analyze_trends(keywords: list) -> Dict[str, Any]:
    """
    Analyze current trends relevant to given keywords
    This is a helper function for more sophisticated trend integration
    """
    # Placeholder for trend analysis
    # In production, this could integrate with Google Trends API, social media APIs, etc.
    
    sample_trends = {
        "fitness": ["morning routines", "workout challenges", "healthy lifestyle"],
        "technology": ["AI integration", "productivity hacks", "digital wellness"], 
        "food": ["sustainable eating", "meal prep", "local ingredients"],
        "fashion": ["sustainable fashion", "versatile pieces", "personal style"]
    }
    
    relevant_trends = []
    for keyword in keywords:
        for category, trends in sample_trends.items():
            if keyword.lower() in category or any(keyword.lower() in trend for trend in trends):
                relevant_trends.extend(trends)
    
    return {
        "trending_topics": list(set(relevant_trends)),
        "relevance_score": len(relevant_trends) / len(keywords) if keywords else 0,
        "last_updated": "2024-01-01"  # In production, use actual timestamp
    }
