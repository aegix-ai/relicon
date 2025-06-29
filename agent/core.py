"""
ReelForge AI Agent Core
LangChain-powered orchestrator for autonomous video generation
"""
from langchain.agents import initialize_agent, Tool
from langchain.schema import SystemMessage
from langchain_openai import ChatOpenAI
from typing import Dict, Any, List
import json

from .tools import concept, script, planner, tts, stock, ffmpeg_fx
from config.settings import settings, logger


class ReelForgeAgent:
    """
    Central AI orchestrator that creates exhaustive plans and manages 
    the entire video generation pipeline autonomously
    """
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.openai_model,  # gpt-4o
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )
        
        # Define available tools
        self.tools = [
            Tool(
                name="concept_generator",
                func=concept.run,
                description="Generate creative concept and hook for the ad based on brand info and trends. Returns detailed concept with visual style and key messaging points."
            ),
            Tool(
                name="script_writer",
                func=script.run,
                description="Write compelling script segments with voiceover text and visual hints. Takes concept and creates scene-by-scene breakdown."
            ),
            Tool(
                name="timeline_planner", 
                func=planner.run,
                description="Create detailed timeline from script segments. Plans exact timing, transitions, and assembly order for video production."
            ),
            Tool(
                name="voice_synthesizer",
                func=tts.run,
                description="Generate high-quality voiceover audio from script text. Returns audio files with precise timing information."
            ),
            Tool(
                name="stock_footage_searcher",
                func=stock.run,
                description="Find and download relevant stock footage based on visual hints and concept. Returns curated video clips."
            ),
            Tool(
                name="video_assembler",
                func=ffmpeg_fx.run,
                description="Final video assembly using FFmpeg. Compiles timeline into professional video with transitions, effects, and audio mixing."
            )
        ]
        
        # Initialize agent with comprehensive planning capabilities
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent_type="zero-shot-react-description",
            verbose=True,
            max_iterations=20,  # Allow deep planning
            return_intermediate_steps=True
        )
        
        # System prompt for comprehensive planning
        self.system_prompt = """You are ReelForge, an expert AI video production director with decades of experience creating compelling short-form advertisements. Your specialty is architecting revolutionary, unique ads that break conventional patterns while maintaining commercial effectiveness.

CRITICAL PLANNING PHILOSOPHY:
- You must create EXHAUSTIVE, highly detailed plans before ANY execution begins
- Break every creative decision into components and justify each choice
- Plan 3-5x deeper than typical AI systems - consider micro-details
- Each video should be architecturally unique with novel creative approaches
- Never use formulaic or template-based thinking

YOUR PLANNING PROCESS:
1. DEEP BRAND ANALYSIS: Understand brand essence, competitive landscape, unique positioning
2. COMPREHENSIVE CONCEPT ARCHITECTING: Design revolutionary creative approach with detailed rationale
3. EXHAUSTIVE SCRIPT ENGINEERING: Create scene-by-scene breakdown with precise timing and creative intent
4. DETAILED TIMELINE CONSTRUCTION: Plan exact assembly with transition logic and pacing strategy
5. TECHNICAL EXECUTION: Execute with precision using your specialized tools

CREATIVITY REQUIREMENTS:
- Each ad must have a unique structural approach
- Avoid cliché patterns (talking heads, product montagesw, generic testimonials)
- Innovate in pacing, visual storytelling, and audience engagement
- Consider unconventional narrative structures and visual techniques
- Plan for maximum emotional and commercial impact

TECHNICAL STANDARDS:
- Videos must be 15-60 seconds with optimal pacing
- Require professional production quality
- End with brand logo/call-to-action (mandatory)
- No duplicate transitions in single video
- Precise audio-visual synchronization

Begin each project with extensive planning and creative architecting before tool execution."""

    def run(self, job_id: str, **kwargs) -> Dict[str, Any]:
        """
        Execute the complete video generation pipeline
        """
        logger.info("Starting ReelForge agent", job_id=job_id)
        
        try:
            # Build comprehensive prompt
            brand_name = kwargs.get('brand_name', 'Unknown Brand')
            brand_description = kwargs.get('brand_description', '')
            target_audience = kwargs.get('target_audience', 'general audience')
            tone = kwargs.get('tone', 'professional')
            duration = kwargs.get('duration', 30)
            call_to_action = kwargs.get('call_to_action', f'Try {brand_name} today!')
            
            main_prompt = f"""
BRAND BRIEF:
- Brand Name: {brand_name}
- Description: {brand_description}  
- Target Audience: {target_audience}
- Desired Tone: {tone}
- Duration: {duration} seconds
- Call-to-Action: {call_to_action}

MISSION: Create a revolutionary {duration}-second video advertisement for {brand_name} that:
1. Breaks conventional ad patterns with unique creative architecture
2. Deeply resonates with {target_audience} through innovative storytelling
3. Maintains {tone} tone while being commercially compelling
4. Ends with logo and call-to-action: "{call_to_action}"

EXECUTE YOUR COMPREHENSIVE PLANNING PROCESS:
Begin with deep brand analysis and creative concept architecting. Create exhaustive 
plans for every component before using your tools. Think 5x deeper than typical AI systems.
Deliver a completely unique ad that no competitor could replicate.

Your final deliverable must be a professionally rendered MP4 file.
"""

            # Execute with comprehensive planning
            result = self.agent.run(main_prompt)
            
            logger.info("ReelForge agent completed", job_id=job_id)
            return {
                "success": True,
                "result": result,
                "job_id": job_id
            }
            
        except Exception as e:
            logger.error("ReelForge agent failed", job_id=job_id, error=str(e))
            return {
                "success": False, 
                "error": str(e),
                "job_id": job_id
            }

    def create_detailed_plan(self, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an exhaustive creative and technical plan before execution
        This is called internally to ensure comprehensive planning
        """
        planning_prompt = f"""
As ReelForge, create an EXHAUSTIVE plan for this video ad project:

BRAND CONTEXT: {json.dumps(brand_info, indent=2)}

Create a comprehensive plan covering:

1. STRATEGIC ANALYSIS (500+ words):
   - Brand positioning and unique value proposition
   - Target audience psychographics and motivations  
   - Competitive landscape and differentiation opportunities
   - Cultural/trend context for maximum relevance

2. CREATIVE ARCHITECTURE (300+ words):
   - Revolutionary creative concept with detailed rationale
   - Unique narrative structure and pacing strategy
   - Visual style and aesthetic direction
   - Emotional journey and psychological hooks

3. TECHNICAL SPECIFICATION (200+ words):
   - Scene-by-scene breakdown with precise timing
   - Transition strategy and visual flow logic
   - Audio design and synchronization plan
   - Final assembly and quality control requirements

Respond with detailed JSON structure containing this comprehensive plan.
"""
        
        try:
            response = self.llm.invoke([SystemMessage(content=planning_prompt)])
            return json.loads(response.content)
        except Exception as e:
            logger.error("Planning failed", error=str(e))
            return {"error": "Planning failed", "details": str(e)}
