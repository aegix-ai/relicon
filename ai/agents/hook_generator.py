"""
AI Agent for generating next-generation hooks based on winning ads
Analyzes performance data and generates optimized hooks
"""
import json
from typing import Dict, List, Any
from pydantic import BaseModel
from openai import OpenAI
from config.settings import settings

class NextGenHook(BaseModel):
    """Schema for next-generation hook suggestions"""
    hook_text: str
    hook_type: str  # "question", "statement", "statistic", "emotional"
    target_emotion: str  # "curiosity", "urgency", "desire", "fear", "excitement"
    platform_optimized: str  # "meta", "tiktok", "universal"
    confidence_score: float  # 0.0 to 1.0

class NextGenHooks(BaseModel):
    """Collection of next-generation hooks"""
    hooks: List[NextGenHook]
    analysis_summary: str
    winning_patterns: List[str]

class HookGenerator:
    """AI agent for generating optimized hooks"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_next_gen_hooks(self, winner_ads: List[Dict], current_ad: Dict) -> Dict[str, Any]:
        """Generate next-generation hooks using AI analysis of winning ads"""
        try:
            # Analyze winning patterns
            winning_patterns = self._analyze_winning_patterns(winner_ads)
            
            # Generate hooks based on patterns
            hooks = self._generate_hooks_from_patterns(winning_patterns, current_ad)
            
            # Create analysis summary
            analysis_summary = self._create_analysis_summary(winner_ads, winning_patterns)
            
            return {
                "hooks": hooks,
                "analysis_summary": analysis_summary,
                "winning_patterns": winning_patterns
            }
            
        except Exception as e:
            print(f"Error generating hooks: {e}")
            return self._generate_fallback_hooks(current_ad)
    
    def _analyze_winning_patterns(self, winner_ads: List[Dict]) -> List[str]:
        """Analyze winning ads to identify patterns"""
        if not winner_ads:
            return ["No winning ads data available"]
        
        # Extract creative content from winner ads
        creative_content = []
        for ad in winner_ads:
            if hasattr(ad, 'creative_content') and ad.creative_content:
                creative_content.append(ad.creative_content)
        
        if not creative_content:
            return ["No creative content available from winning ads"]
        
        try:
            prompt = f"""
            Analyze these winning ad creatives and identify the top 5 patterns that make them successful:
            
            {chr(10).join(creative_content)}
            
            Focus on:
            1. Hook patterns and opening lines
            2. Emotional triggers used
            3. Call-to-action styles
            4. Storytelling techniques
            5. Urgency and scarcity tactics
            
            Return only the top 5 patterns as a JSON array of strings.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("patterns", [])
            
        except Exception as e:
            print(f"Error analyzing patterns: {e}")
            return ["Pattern analysis failed"]
    
    def _generate_hooks_from_patterns(self, patterns: List[str], current_ad: Dict) -> List[Dict]:
        """Generate hooks based on identified patterns"""
        try:
            prompt = f"""
            Based on these winning patterns:
            {chr(10).join(patterns)}
            
            And this current ad context:
            Platform: {getattr(current_ad, 'platform', 'unknown')}
            Creative: {getattr(current_ad, 'creative_content', 'No content')}
            
            Generate 5 optimized hooks in JSON format:
            {{
                "hooks": [
                    {{
                        "hook_text": "...",
                        "hook_type": "question|statement|statistic|emotional",
                        "target_emotion": "curiosity|urgency|desire|fear|excitement",
                        "platform_optimized": "meta|tiktok|universal",
                        "confidence_score": 0.0-1.0
                    }}
                ]
            }}
            
            Make hooks engaging, platform-appropriate, and based on winning patterns.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("hooks", [])
            
        except Exception as e:
            print(f"Error generating hooks: {e}")
            return self._get_fallback_hooks()
    
    def _create_analysis_summary(self, winner_ads: List[Dict], patterns: List[str]) -> str:
        """Create summary of analysis"""
        if not winner_ads:
            return "No winning ads data available for analysis"
        
        return f"""
        Analysis of {len(winner_ads)} winning ads revealed key patterns:
        
        Top Patterns:
        {chr(10).join(f"• {pattern}" for pattern in patterns[:3])}
        
        Recommendations:
        • Focus on emotional triggers that drove high performance
        • Implement winning hook structures in new creatives
        • Test variations of top-performing patterns
        """
    
    def _generate_fallback_hooks(self, current_ad: Dict) -> Dict[str, Any]:
        """Generate fallback hooks when main generation fails"""
        fallback_hooks = self._get_fallback_hooks()
        
        return {
            "hooks": fallback_hooks,
            "analysis_summary": "Generated fallback hooks due to analysis limitations",
            "winning_patterns": ["Generic high-performing patterns applied"]
        }
    
    def _get_fallback_hooks(self) -> List[Dict]:
        """Get basic fallback hooks"""
        return [
            {
                "hook_text": "Have you ever wondered why this works so well?",
                "hook_type": "question",
                "target_emotion": "curiosity",
                "platform_optimized": "universal",
                "confidence_score": 0.7
            },
            {
                "hook_text": "This changes everything you thought you knew...",
                "hook_type": "statement",
                "target_emotion": "excitement",
                "platform_optimized": "universal",
                "confidence_score": 0.6
            },
            {
                "hook_text": "Don't miss out on this opportunity!",
                "hook_type": "emotional",
                "target_emotion": "urgency",
                "platform_optimized": "universal",
                "confidence_score": 0.5
            }
        ]

# Global hook generator instance
hook_generator = HookGenerator()

# Legacy function for backwards compatibility
def generate_next_gen_hooks(winner_ads: List[Dict], current_ad: Dict) -> Dict[str, Any]:
    """Generate next-generation hooks (legacy wrapper)"""
    return hook_generator.generate_next_gen_hooks(winner_ads, current_ad)