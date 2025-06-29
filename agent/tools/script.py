"""
Script Writing Tool
Creates detailed scripts with voiceover segments and visual hints
"""
import json
import os
from openai import OpenAI

class ScriptWritingTool:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def run(self, input_data: str) -> str:
        try:
            data = json.loads(input_data)
            concept = data.get('concept', {})
            brand_info = data.get('brand_info', {})
            
            prompt = f"""
            Write a detailed script for a video ad based on this concept:
            
            Concept: {concept.get('concept', 'No concept provided')}
            Hook: {concept.get('hook', 'No hook provided')}
            Duration: {brand_info.get('duration', 30)} seconds
            
            Create a script with precise segments including:
            - Voiceover text for each segment
            - Visual descriptions for each scene
            - Timing recommendations
            - Transition suggestions
            
            Respond with JSON containing an array of script segments.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional script writer specializing in compelling video ads."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return json.dumps({
                "error": f"Script writing failed: {str(e)}",
                "status": "failed"
            })