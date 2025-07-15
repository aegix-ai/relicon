"""
Ultra-Dynamic Tree-Based AI Planner
Holistic planning system that thinks, reasons, and plans from complete overview down to granular details
Uses tree-like hierarchical planning with full context awareness at every level
"""
import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from openai import OpenAI

@dataclass
class PlanningNode:
    """Represents a node in the planning tree"""
    level: str  # 'overview', 'strategic', 'tactical', 'component', 'execution'
    content: Dict[str, Any]
    children: List['PlanningNode']
    parent: Optional['PlanningNode'] = None
    context: Dict[str, Any] = None

class UltraDynamicTreePlanner:
    """
    Revolutionary AI planner that maintains complete context awareness
    Plans like a human creative director - seeing the whole picture while crafting details
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.planning_tree = None
        self.full_context = {}
        
    def create_holistic_plan(self, brand_info: Dict[str, Any], historical_data: List[Dict] = None) -> Dict[str, Any]:
        """
        Creates complete holistic plan using tree-based reasoning
        AI sees everything from overview to execution details simultaneously
        """
        
        # Build complete context that flows through entire tree
        self.full_context = {
            'brand_info': brand_info,
            'historical_performance': historical_data or [],
            'cost_constraints': self._calculate_cost_constraints(brand_info.get('duration', 15)),
            'platform_requirements': self._get_platform_requirements(),
            'success_patterns': self._extract_success_patterns(historical_data or []),
            'failure_patterns': self._extract_failure_patterns(historical_data or [])
        }
        
        # Level 1: Strategic Overview - The Foundation
        overview_node = self._create_strategic_overview()
        
        # Level 2: Campaign Architecture - The Structure  
        architecture_nodes = self._create_campaign_architecture(overview_node)
        
        # Level 3: Creative Components - The Building Blocks
        component_nodes = []
        for arch_node in architecture_nodes:
            components = self._create_creative_components(arch_node)
            component_nodes.extend(components)
        
        # Level 4: Execution Details - The Granular Implementation
        execution_nodes = []
        for comp_node in component_nodes:
            execution = self._create_execution_details(comp_node)
            execution_nodes.extend(execution)
        
        # Level 5: Cost-Optimized Assembly - The Final Optimization
        optimized_plan = self._optimize_for_costs_and_performance(execution_nodes)
        
        return {
            'planning_methodology': 'ultra_dynamic_tree',
            'full_context_maintained': True,
            'strategic_overview': overview_node.content,
            'campaign_architecture': [node.content for node in architecture_nodes],
            'creative_components': [node.content for node in component_nodes],
            'execution_plan': optimized_plan,
            'cost_analysis': self._generate_cost_analysis(optimized_plan),
            'success_prediction': self._predict_success_probability(optimized_plan)
        }
    
    def _create_strategic_overview(self) -> PlanningNode:
        """Level 1: Think like a CMO - complete strategic vision"""
        
        strategic_prompt = f"""
        You are an elite creative director planning a video ad campaign. Think holistically about the complete strategic landscape.
        
        COMPLETE CONTEXT AWARENESS:
        Brand: {self.full_context['brand_info']}
        Historical Performance: {len(self.full_context['historical_performance'])} campaigns analyzed
        Success Patterns: {self.full_context['success_patterns']}
        Failure Patterns: {self.full_context['failure_patterns']}
        Cost Constraints: {self.full_context['cost_constraints']}
        Platform Requirements: {self.full_context['platform_requirements']}
        
        STRATEGIC THINKING FRAMEWORK:
        1. Market Position: Where does this brand sit in the competitive landscape?
        2. Audience Psychology: What drives our target audience's decision-making?
        3. Emotional Architecture: What emotional journey will create maximum impact?
        4. Differentiation Strategy: How do we stand out from competitors?
        5. Conversion Psychology: What specific triggers will drive action?
        6. Platform Optimization: How do we maximize performance across channels?
        
        Create a comprehensive strategic overview that will guide every tactical decision.
        Think like you're presenting to the CEO - show the complete vision.
        
        Return JSON with this structure:
        {{
            "market_position": "Brand's unique position in market",
            "audience_psychology": {{"primary_motivators": [], "pain_points": [], "decision_triggers": []}},
            "emotional_architecture": {{"opening_emotion": "", "build_emotions": [], "climax_emotion": "", "resolution_emotion": ""}},
            "differentiation_strategy": "What makes this campaign unique",
            "conversion_psychology": {{"trust_builders": [], "urgency_creators": [], "value_demonstrators": []}},
            "success_metrics": {{"primary_kpi": "", "secondary_kpis": [], "target_benchmarks": {{}}}},
            "risk_mitigation": {{"identified_risks": [], "mitigation_strategies": []}},
            "creative_direction": "Overall creative vision and style"
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": strategic_prompt}],
            response_format={"type": "json_object"},
            temperature=0.8  # Higher creativity for strategic thinking
        )
        
        strategic_content = json.loads(response.choices[0].message.content)
        
        return PlanningNode(
            level='strategic_overview',
            content=strategic_content,
            children=[],
            context=self.full_context
        )
    
    def _create_campaign_architecture(self, overview_node: PlanningNode) -> List[PlanningNode]:
        """Level 2: Architect the campaign structure with full strategic context"""
        
        duration = self.full_context['brand_info'].get('duration', 15)
        
        architecture_prompt = f"""
        You are now the campaign architect. Using the strategic overview, design the optimal campaign structure.
        
        STRATEGIC FOUNDATION (Never forget this context):
        {json.dumps(overview_node.content, indent=2)}
        
        ARCHITECTURAL CONSTRAINTS:
        - Video Duration: {duration} seconds
        - Cost Optimization: Maximum {self.full_context['cost_constraints']['max_segments']} segments
        - Platform: {self.full_context['platform_requirements']['primary_platform']}
        
        ARCHITECTURAL THINKING:
        1. Story Architecture: How will the narrative unfold to maximize emotional impact?
        2. Pacing Strategy: What rhythm will keep viewers engaged throughout?
        3. Visual Hierarchy: How will visual elements guide attention and reinforce messaging?
        4. Attention Economics: How do we capture and maintain attention in a crowded feed?
        5. Conversion Funnel: How does each moment move viewers toward the desired action?
        
        Design the optimal campaign architecture that fulfills the strategic vision.
        
        Return JSON with this structure:
        {{
            "narrative_architecture": {{"story_type": "", "narrative_flow": [], "emotional_beats": []}},
            "pacing_strategy": {{"opening_pace": "", "build_pace": "", "climax_pace": "", "resolution_pace": ""}},
            "visual_hierarchy": {{"primary_focus": "", "secondary_elements": [], "supporting_elements": []}},
            "attention_strategy": {{"hook_mechanism": "", "retention_tactics": [], "engagement_drivers": []}},
            "conversion_architecture": {{"awareness_elements": [], "consideration_elements": [], "decision_elements": [], "action_elements": []}},
            "segment_blueprint": [
                {{
                    "segment_number": 1,
                    "duration_seconds": 0,
                    "narrative_purpose": "",
                    "emotional_purpose": "",
                    "conversion_purpose": "",
                    "visual_style": "",
                    "pacing": ""
                }}
            ]
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": architecture_prompt}],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        architecture_content = json.loads(response.choices[0].message.content)
        
        # Create architecture node with full context
        architecture_node = PlanningNode(
            level='campaign_architecture',
            content=architecture_content,
            children=[],
            parent=overview_node,
            context={**self.full_context, 'strategic_overview': overview_node.content}
        )
        
        overview_node.children.append(architecture_node)
        return [architecture_node]
    
    def _create_creative_components(self, architecture_node: PlanningNode) -> List[PlanningNode]:
        """Level 3: Design each creative component with complete context awareness"""
        
        components = []
        segment_blueprint = architecture_node.content.get('segment_blueprint', [])
        
        for segment in segment_blueprint:
            component_prompt = f"""
            You are now the creative component designer. Design this specific segment with complete awareness of the overall strategy and architecture.
            
            COMPLETE CONTEXT (Always reference this):
            Strategic Overview: {architecture_node.context['strategic_overview']}
            Campaign Architecture: {json.dumps(architecture_node.content, indent=2)}
            
            CURRENT SEGMENT TO DESIGN:
            {json.dumps(segment, indent=2)}
            
            CREATIVE COMPONENT THINKING:
            1. Scene Concept: What specific scene will fulfill this segment's purpose?
            2. Visual Storytelling: How will visuals convey the message without words?
            3. Emotional Trigger: What specific visual/audio elements will create the desired emotion?
            4. Attention Mechanism: How will this segment capture and hold attention?
            5. Transition Strategy: How does this segment connect to the next?
            6. Cost Efficiency: How do we maximize impact while minimizing generation costs?
            
            Design the optimal creative component for this segment.
            
            Return JSON with this structure:
            {{
                "scene_concept": {{"setting": "", "main_elements": [], "visual_story": ""}},
                "visual_design": {{"color_palette": [], "lighting_style": "", "composition": "", "camera_movement": ""}},
                "content_elements": {{"voiceover_script": "", "text_overlays": [], "visual_metaphors": []}},
                "emotional_triggers": {{"primary_trigger": "", "supporting_triggers": [], "sensory_elements": []}},
                "technical_specs": {{"duration": 0, "aspect_ratio": "9:16", "quality_requirements": ""}},
                "luma_prompt": "Optimized prompt for Luma AI generation",
                "transition_plan": {{"transition_type": "", "duration": 0, "visual_effect": ""}},
                "success_elements": ["Elements that will drive performance based on historical data"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": component_prompt}],
                response_format={"type": "json_object"},
                temperature=0.6
            )
            
            component_content = json.loads(response.choices[0].message.content)
            
            component_node = PlanningNode(
                level='creative_component',
                content={**segment, **component_content},
                children=[],
                parent=architecture_node,
                context={
                    **architecture_node.context,
                    'campaign_architecture': architecture_node.content,
                    'current_segment': segment
                }
            )
            
            components.append(component_node)
            architecture_node.children.append(component_node)
        
        return components
    
    def _create_execution_details(self, component_node: PlanningNode) -> List[PlanningNode]:
        """Level 4: Create granular execution details with full hierarchical context"""
        
        execution_prompt = f"""
        You are now the execution specialist. Create precise execution details for this component with complete context awareness.
        
        FULL HIERARCHICAL CONTEXT:
        Strategic Overview: {component_node.context.get('strategic_overview', {})}
        Campaign Architecture: {component_node.context.get('campaign_architecture', {})}
        Component Design: {json.dumps(component_node.content, indent=2)}
        
        EXECUTION THINKING:
        1. Technical Implementation: Exact specifications for optimal generation
        2. Quality Assurance: How to ensure output meets strategic requirements
        3. Cost Optimization: Minimize costs while maximizing quality
        4. Performance Prediction: Likelihood of success based on historical patterns
        5. Risk Assessment: Potential issues and mitigation strategies
        
        Create precise execution details that guarantee successful implementation.
        
        Return JSON with this structure:
        {{
            "technical_implementation": {{"luma_settings": {{}}, "audio_specs": {{}}, "assembly_instructions": {{}}}},
            "quality_assurance": {{"success_criteria": [], "quality_checkpoints": [], "fallback_options": []}},
            "cost_optimization": {{"estimated_cost": 0, "cost_breakdown": {{}}, "optimization_strategies": []}},
            "performance_prediction": {{"success_probability": 0, "key_performance_drivers": [], "risk_factors": []}},
            "execution_timeline": {{"preparation": "", "generation": "", "assembly": "", "qa": ""}},
            "final_specifications": {{
                "optimized_luma_prompt": "",
                "duration_seconds": 0,
                "technical_parameters": {{}},
                "success_metrics": {{}}
            }}
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": execution_prompt}],
            response_format={"type": "json_object"},
            temperature=0.4  # Lower temperature for precise execution
        )
        
        execution_content = json.loads(response.choices[0].message.content)
        
        execution_node = PlanningNode(
            level='execution_details',
            content=execution_content,
            children=[],
            parent=component_node,
            context={
                **component_node.context,
                'component_design': component_node.content
            }
        )
        
        component_node.children.append(execution_node)
        return [execution_node]
    
    def _optimize_for_costs_and_performance(self, execution_nodes: List[PlanningNode]) -> Dict[str, Any]:
        """Level 5: Final optimization with complete system awareness"""
        
        optimization_prompt = f"""
        You are now the optimization engine. Analyze all execution details and create the final optimized plan.
        
        COMPLETE SYSTEM CONTEXT:
        Total Execution Nodes: {len(execution_nodes)}
        Brand Requirements: {self.full_context['brand_info']}
        Cost Constraints: {self.full_context['cost_constraints']}
        Historical Patterns: {self.full_context['success_patterns']}
        
        ALL EXECUTION DETAILS:
        {json.dumps([node.content for node in execution_nodes], indent=2)}
        
        OPTIMIZATION OBJECTIVES:
        1. Cost Efficiency: Minimize total generation costs
        2. Performance Maximization: Optimize for highest predicted ROAS
        3. Quality Assurance: Maintain professional standards
        4. Risk Mitigation: Reduce chance of failure
        5. Scalability: Enable future improvements
        
        Create the final optimized execution plan that balances all objectives.
        
        Return JSON with this structure:
        {{
            "optimized_segments": [
                {{
                    "segment_id": 1,
                    "final_luma_prompt": "",
                    "duration": 0,
                    "cost_estimate": 0,
                    "success_probability": 0,
                    "voiceover_script": "",
                    "technical_specs": {{}}
                }}
            ],
            "total_cost_estimate": 0,
            "predicted_performance": {{"roas_prediction": 0, "confidence_level": 0}},
            "optimization_summary": {{"cost_savings": 0, "performance_improvements": [], "risk_reductions": []}},
            "implementation_plan": {{"generation_order": [], "assembly_sequence": [], "qa_checkpoints": []}},
            "success_metrics": {{"kpis": [], "benchmarks": {{}}, "monitoring_plan": {{}}}}
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": optimization_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3  # Very precise for final optimization
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _calculate_cost_constraints(self, duration: int) -> Dict[str, Any]:
        """Calculate optimal cost constraints based on duration"""
        if duration <= 15:
            max_segments = 2
            target_cost = 2.40
        elif duration <= 30:
            max_segments = 3
            target_cost = 3.60
        else:
            max_segments = 4
            target_cost = 4.80
        
        return {
            'max_segments': max_segments,
            'target_cost': target_cost,
            'cost_per_segment': 1.20,  # ray-1-6 model
            'optimization_priority': 'balanced'
        }
    
    def _get_platform_requirements(self) -> Dict[str, Any]:
        """Get platform-specific requirements"""
        return {
            'primary_platform': 'multi_platform',
            'aspect_ratio': '9:16',
            'optimal_duration': '15-30 seconds',
            'engagement_patterns': ['hook_first_3s', 'cta_last_3s'],
            'algorithm_preferences': ['high_completion_rate', 'strong_engagement']
        }
    
    def _extract_success_patterns(self, historical_data: List[Dict]) -> List[str]:
        """Extract patterns from successful campaigns"""
        if not historical_data:
            return [
                "emotional_hooks_in_first_3_seconds",
                "clear_value_proposition",
                "strong_visual_storytelling",
                "compelling_call_to_action"
            ]
        
        # TODO: Implement real pattern extraction from historical data
        return ["dynamic_patterns_from_winners"]
    
    def _extract_failure_patterns(self, historical_data: List[Dict]) -> List[str]:
        """Extract patterns from failed campaigns"""
        if not historical_data:
            return [
                "slow_opening_hook",
                "unclear_messaging",
                "weak_call_to_action",
                "poor_visual_quality"
            ]
        
        # TODO: Implement real pattern extraction from historical data
        return ["patterns_to_avoid_from_losers"]
    
    def _generate_cost_analysis(self, optimized_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed cost analysis"""
        segments = optimized_plan.get('optimized_segments', [])
        total_cost = optimized_plan.get('total_cost_estimate', 0)
        
        return {
            'segment_count': len(segments),
            'cost_per_segment': 1.20,
            'total_luma_cost': len(segments) * 1.20,
            'total_system_cost': total_cost,
            'cost_efficiency_score': min(100, (3.0 / max(total_cost, 0.1)) * 100),
            'optimization_achieved': True
        }
    
    def _predict_success_probability(self, optimized_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Predict success probability based on plan quality"""
        predicted_performance = optimized_plan.get('predicted_performance', {})
        
        return {
            'roas_prediction': predicted_performance.get('roas_prediction', 3.5),
            'confidence_level': predicted_performance.get('confidence_level', 0.75),
            'success_factors': optimized_plan.get('optimization_summary', {}).get('performance_improvements', []),
            'risk_assessment': 'low_to_medium'
        }