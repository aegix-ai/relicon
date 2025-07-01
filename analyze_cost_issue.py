#!/usr/bin/env python3
"""
Analyze the $8 cost issue for 24-second video generation
"""
import json
import os
from ai_planner import VideoAdPlanner

def analyze_cost_breakdown():
    """Analyze what caused the high cost"""
    
    print("🔍 COST ANALYSIS REPORT")
    print("=" * 50)
    
    # Test the same brand info that was used
    brand_info = {
        "brand_name": "TechFlow", 
        "brand_description": "Innovative productivity app for modern teams",
        "target_audience": "business professionals",
        "tone": "professional",
        "duration": 15  # This was the requested duration
    }
    
    print("1. ANALYZING AI PLANNING LOGIC")
    print("-" * 30)
    
    planner = VideoAdPlanner()
    
    # Step 1: Check master plan
    print("Creating master plan...")
    master_plan = planner.create_master_plan(brand_info)
    print(f"✓ Master plan created")
    
    # Step 2: Check component breakdown 
    print("Breaking down into components...")
    components = planner.break_down_components(master_plan, duration=15)
    print(f"✓ Scene count: {len(components)} scenes")
    
    total_planned_duration = 0
    for i, scene in enumerate(components):
        duration = scene.get('duration', 5)
        total_planned_duration += duration
        print(f"  Scene {i+1}: {duration}s - {scene.get('purpose')} - {scene.get('message')}")
    
    print(f"✓ Total planned duration: {total_planned_duration}s")
    
    # This is the CRITICAL issue - check if we're creating too many segments
    print("\n2. LUMA AI COST BREAKDOWN")
    print("-" * 30)
    
    # Luma AI pricing (estimate based on typical AI video costs):
    # Each video segment likely costs $1-2 regardless of duration
    estimated_cost_per_segment = 1.5  # Conservative estimate
    total_estimated_cost = len(components) * estimated_cost_per_segment
    
    print(f"Number of video segments: {len(components)}")
    print(f"Estimated cost per segment: ${estimated_cost_per_segment}")
    print(f"Total estimated cost: ${total_estimated_cost}")
    print(f"Actual cost reported: $8.00")
    
    if total_estimated_cost > 6:
        print("\n🚨 PROBLEM IDENTIFIED: TOO MANY SEGMENTS")
        print("The AI planner is creating too many individual video segments!")
        print("Each Luma AI generation costs regardless of duration.")
        print("Solution: Optimize to create fewer, longer segments.")
    
    print("\n3. OPTIMIZATION RECOMMENDATIONS")
    print("-" * 30)
    
    # Calculate optimal segmentation
    target_duration = brand_info.get('duration', 15)
    
    if target_duration <= 15:
        optimal_segments = 2  # 2 segments max for short videos
        print(f"For {target_duration}s video, use max 2 segments:")
        print(f"  - Segment 1: {target_duration//2}s (hook + build)")
        print(f"  - Segment 2: {target_duration - target_duration//2}s (climax + CTA)")
        print(f"  Estimated cost: ${2 * estimated_cost_per_segment}")
    elif target_duration <= 30:
        optimal_segments = 3  # 3 segments max for medium videos
        print(f"For {target_duration}s video, use max 3 segments:")
        print(f"  Estimated cost: ${3 * estimated_cost_per_segment}")
    else:
        optimal_segments = 4  # 4 segments max even for long videos
        print(f"For {target_duration}s video, use max 4 segments:")
        print(f"  Estimated cost: ${4 * estimated_cost_per_segment}")
    
    print(f"\n4. CURRENT VS OPTIMAL")
    print("-" * 30)
    print(f"Current segments: {len(components)} → ~${len(components) * estimated_cost_per_segment}")
    print(f"Optimal segments: {optimal_segments} → ~${optimal_segments * estimated_cost_per_segment}")
    print(f"Potential savings: ${(len(components) - optimal_segments) * estimated_cost_per_segment}")
    
    return {
        'current_segments': len(components),
        'optimal_segments': optimal_segments,
        'estimated_current_cost': len(components) * estimated_cost_per_segment,
        'estimated_optimal_cost': optimal_segments * estimated_cost_per_segment
    }

if __name__ == "__main__":
    analyze_cost_breakdown()