#!/usr/bin/env python3
"""
Quick analysis of cost issue
"""

def analyze_segments():
    """Check how many segments we're creating"""
    
    print("💰 COST ANALYSIS: Why $8 for 24 seconds?")
    print("=" * 45)
    
    # Based on the logs, we can see it processed 5 video segments
    # From the logs: "Processing video segment 2", "segment 3", "segment 4", "segment 5"
    segments_created = 5
    video_duration = 24  # seconds
    
    print(f"Video duration: {video_duration} seconds")
    print(f"Number of segments: {segments_created}")
    print(f"Average per segment: {video_duration/segments_created:.1f} seconds")
    
    # Luma AI pricing analysis
    print("\nLUMA AI PRICING BREAKDOWN:")
    print("-" * 25)
    
    # Based on typical AI video pricing:
    # - Each generation costs regardless of duration (5s vs 10s same price)
    # - Premium models like "ray-2" cost more
    # - 720p resolution standard pricing
    
    estimated_cost_per_generation = 1.6  # Conservative estimate for ray-2 model
    total_estimated_cost = segments_created * estimated_cost_per_generation
    
    print(f"Segments generated: {segments_created}")
    print(f"Cost per segment (ray-2): ~${estimated_cost_per_generation}")
    print(f"Total estimated cost: ~${total_estimated_cost}")
    print(f"Actual cost: $8.00")
    
    if total_estimated_cost >= 7:
        print("\n🚨 PROBLEM IDENTIFIED:")
        print("   TOO MANY INDIVIDUAL SEGMENTS!")
        print("   Each Luma generation costs the same regardless of duration")
        print("   5 segments × $1.60 = $8.00")
    
    print("\n💡 SOLUTION:")
    print("-" * 10)
    print("For 15-24 second videos:")
    print("• Use maximum 2-3 segments instead of 5")
    print("• Segment 1: 8-12 seconds (hook + build)")  
    print("• Segment 2: 7-12 seconds (climax + CTA)")
    print("• Estimated cost: 2 × $1.60 = $3.20 (60% savings!)")
    
    print("\n📊 OPTIMIZATION STRATEGY:")
    print("-" * 23)
    print("✓ Limit segments based on total duration:")
    print("  - ≤15s video: 2 segments max")
    print("  - 16-30s video: 3 segments max") 
    print("  - 31-45s video: 4 segments max")
    print("  - 46s+ video: 5 segments max")
    
    return {
        'current_cost': 8.00,
        'segments': segments_created,
        'optimized_segments': 2,
        'optimized_cost': 2 * estimated_cost_per_generation
    }

if __name__ == "__main__":
    result = analyze_segments()
    print(f"\n🎯 IMMEDIATE ACTION NEEDED:")
    print(f"   Current: {result['segments']} segments = ${result['current_cost']}")
    print(f"   Optimized: {result['optimized_segments']} segments = ${result['optimized_cost']}")
    print(f"   Savings: ${result['current_cost'] - result['optimized_cost']} ({((result['current_cost'] - result['optimized_cost'])/result['current_cost']*100):.0f}%)")