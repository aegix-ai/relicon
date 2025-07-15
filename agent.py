"""AI Agent for generating next-generation hooks based on winning ads."""
import os
import json
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from pydantic import BaseModel
# Configuration using environment variables

from database import Ads


class NextGenHook(BaseModel):
    """Schema for next-generation hook suggestions."""
    hook_text: str
    hook_type: str  # "question", "statement", "statistic", "emotional"
    target_emotion: str  # "curiosity", "urgency", "desire", "fear", "excitement"
    platform_optimized: str  # "meta", "tiktok", "universal"
    confidence_score: float  # 0.0 to 1.0


class NextGenHooks(BaseModel):
    """Collection of next-generation hooks."""
    hooks: List[NextGenHook]
    analysis_summary: str
    winning_patterns: List[str]


# Initialize OpenAI client
llm = ChatOpenAI(
    model="gpt-4o",  # Latest model as per blueprint
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Prompt template for analyzing winning ads and generating hooks
HOOK_GENERATION_PROMPT = PromptTemplate(
    input_variables=["winner_ads", "current_ad", "platform"],
    template="""
You are an elite creative strategist for Relicon AI, specializing in viral advertising hooks.

WINNER ADS ANALYSIS:
{winner_ads}

CURRENT AD TO IMPROVE:
{current_ad}

TARGET PLATFORM: {platform}

TASK: Analyze the winning ads and generate 5 next-generation hooks for the current ad that incorporate the success patterns.

ANALYSIS FRAMEWORK:
1. Identify common patterns in winning ads (emotions, structures, triggers)
2. Extract psychological triggers that drove conversions
3. Analyze platform-specific optimization opportunities
4. Generate hooks that amplify successful elements while staying authentic

HOOK REQUIREMENTS:
- Each hook must be 5-15 words maximum
- Include varied hook types (questions, statements, statistics, emotional)
- Target different emotions (curiosity, urgency, desire, fear, excitement)
- Optimize for the specified platform's algorithm preferences
- Score confidence based on pattern alignment with winners

WINNING PATTERNS TO LOOK FOR:
- Hook structures that generated high ROAS
- Emotional triggers that drove clicks
- Platform-specific formatting that performed well
- Psychological persuasion techniques that converted
- Timing and urgency elements that worked

OUTPUT FORMAT (JSON):
{{
  "hooks": [
    {{
      "hook_text": "Ready to discover the secret?",
      "hook_type": "question",
      "target_emotion": "curiosity",
      "platform_optimized": "meta",
      "confidence_score": 0.87
    }}
  ],
  "analysis_summary": "Winners used curiosity-driven questions with 75% higher ROAS...",
  "winning_patterns": ["Question-based hooks", "Urgency triggers", "Social proof elements"]
}}

Generate strategic, high-converting hooks that build on proven winner patterns.
"""
)


async def generate_next_gen_hooks(winner_ads: List[Ads], current_ad: Ads) -> Dict[str, Any]:
    """Generate next-generation hooks using AI analysis of winning ads."""
    try:
        # Prepare winner ads data for analysis
        winner_data = []
        for ad in winner_ads:
            winner_data.append({
                "ad_id": ad.ad_id,
                "platform": ad.platform,
                "roas": float(ad.roas),
                "creative_content": ad.creative_content or "No content available",
                "winner_tag": ad.winner_tag
            })
        
        # Format current ad data
        current_ad_data = {
            "ad_id": current_ad.ad_id,
            "platform": current_ad.platform,
            "roas": float(current_ad.roas),
            "creative_content": current_ad.creative_content or "No content available",
            "winner_tag": current_ad.winner_tag
        }
        
        # Generate the prompt
        prompt = HOOK_GENERATION_PROMPT.format(
            winner_ads=json.dumps(winner_data, indent=2),
            current_ad=json.dumps(current_ad_data, indent=2),
            platform=current_ad.platform
        )
        
        # Get AI response
        response = llm.invoke([HumanMessage(content=prompt)])
        
        # Parse JSON response
        try:
            hooks_data = json.loads(response.content)
            
            # Validate with Pydantic model
            validated_hooks = NextGenHooks(**hooks_data)
            
            return {
                "hooks": [hook.dict() for hook in validated_hooks.hooks],
                "analysis_summary": validated_hooks.analysis_summary,
                "winning_patterns": validated_hooks.winning_patterns,
                "generation_method": "langchain_openai",
                "model_used": "gpt-4o"
            }
            
        except json.JSONDecodeError:
            # Fallback: create structured response from raw content
            return {
                "hooks": [
                    {
                        "hook_text": "Transform your results today",
                        "hook_type": "statement",
                        "target_emotion": "urgency",
                        "platform_optimized": current_ad.platform,
                        "confidence_score": 0.75
                    }
                ],
                "analysis_summary": f"Generated fallback hooks for {current_ad.ad_id}",
                "winning_patterns": ["Performance-focused messaging"],
                "generation_method": "fallback",
                "raw_ai_response": response.content
            }
        
    except Exception as e:
        print(f"Error in generate_next_gen_hooks: {e}")
        
        # Return fallback response
        return {
            "hooks": [
                {
                    "hook_text": "Discover what works",
                    "hook_type": "statement", 
                    "target_emotion": "curiosity",
                    "platform_optimized": current_ad.platform,
                    "confidence_score": 0.5
                }
            ],
            "analysis_summary": f"Error occurred, generated fallback hooks for {current_ad.ad_id}",
            "winning_patterns": ["Standard messaging approach"],
            "generation_method": "error_fallback",
            "error": str(e)
        }


# Alternative vanilla OpenAI implementation (if LangChain conflicts)
def generate_next_gen_hooks_vanilla(winner_ads: List[Ads], current_ad: Ads) -> Dict[str, Any]:
    """Vanilla OpenAI implementation as fallback."""
    try:
        import openai
        
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Prepare data
        winner_data = [
            {
                "ad_id": ad.ad_id,
                "platform": ad.platform,
                "roas": float(ad.roas),
                "creative_content": ad.creative_content or "No content available"
            }
            for ad in winner_ads
        ]
        
        current_ad_data = {
            "ad_id": current_ad.ad_id,
            "platform": current_ad.platform,
            "roas": float(current_ad.roas),
            "creative_content": current_ad.creative_content or "No content available"
        }
        
        # Create prompt
        prompt = f"""
        Analyze these winning ads and generate 3 next-generation hooks:
        
        Winners: {json.dumps(winner_data, indent=2)}
        Current Ad: {json.dumps(current_ad_data, indent=2)}
        
        Return JSON with hooks array containing hook_text, hook_type, target_emotion, platform_optimized, and confidence_score.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        print(f"Error in vanilla implementation: {e}")
        return {
            "hooks": [
                {
                    "hook_text": "Unlock your potential",
                    "hook_type": "statement",
                    "target_emotion": "desire",
                    "platform_optimized": current_ad.platform,
                    "confidence_score": 0.6
                }
            ],
            "analysis_summary": "Vanilla fallback generated",
            "winning_patterns": ["Motivational messaging"],
            "error": str(e)
        }


if __name__ == "__main__":
    # Test the agent
    print("Agent module loaded successfully!")