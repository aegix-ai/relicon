"""AI script generator for natural human-like voiceovers"""
from typing import Dict, Any, List
from config.settings import settings
import os

class ScriptGenerator:
    """Generates natural, human-like scripts for video content"""
    
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
    
    def generate_energetic_segments(self, brand_info: Dict[str, Any], 
                                  num_segments: int = 3) -> List[Dict[str, Any]]:
        """Generate energetic script segments"""
        try:
            prompt = f"""
            Create a natural, conversational script for a {brand_info.get('duration', 30)}-second video about {brand_info.get('brand_name', 'our product')}.

            Product: {brand_info.get('brand_name', 'Product')}
            Description: {brand_info.get('brand_description', 'Amazing product')}
            
            Requirements:
            - Write like a real person talking naturally
            - Sound conversational, not like reading from a script
            - Keep sentences short and natural
            - Use everyday language
            - Break into {num_segments} segments
            - Each segment should be 8-12 seconds when spoken
            - Make it sound human, not robotic
            
            Format as JSON with segments containing text and approximate duration.
            """
            
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_api_key)
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.7
                )
                
                content = response.choices[0].message.content
                
                # Try to extract JSON, fallback to manual parsing
                try:
                    import json
                    segments = json.loads(content)
                    if isinstance(segments, dict) and 'segments' in segments:
                        return segments['segments']
                    elif isinstance(segments, list):
                        return segments
                except:
                    pass
                    
            except Exception as api_error:
                print(f"OpenAI API error: {api_error}")
                pass
            
            # Fallback: create manual segments
            return self._create_fallback_segments(brand_info, num_segments)
            
        except Exception as e:
            print(f"Script generation error: {e}")
            return self._create_fallback_segments(brand_info, num_segments)
    
    def _create_fallback_segments(self, brand_info: Dict[str, Any], 
                                num_segments: int) -> List[Dict[str, Any]]:
        """Create fallback script segments"""
        brand_name = brand_info.get('brand_name', 'this product')
        description = brand_info.get('brand_description', 'amazing solution')
        
        segments = [
            {
                "text": f"So you know how everyone's talking about {brand_name}? Well, let me tell you why.",
                "duration": 8
            },
            {
                "text": f"This thing is actually {description}. And I'm not just saying that.",
                "duration": 8
            },
            {
                "text": f"Look, if you're interested in {brand_name}, you should definitely check it out.",
                "duration": 8
            }
        ]
        
        return segments[:num_segments]

# Global instance
script_generator = ScriptGenerator()