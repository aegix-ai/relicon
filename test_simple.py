#!/usr/bin/env python3
"""
Simple test to verify ReelForge components work
"""
import os
import json
import sys

# Add current directory to path
sys.path.append('.')

def test_concept_tool():
    """Test the concept generation tool"""
    try:
        from agent.tools.concept import ConceptGenerationTool
        
        tool = ConceptGenerationTool()
        
        # Test with sample data
        test_data = {
            "brand_name": "TechFlow",
            "brand_description": "Modern software solutions for businesses",
            "target_audience": "Business professionals",
            "tone": "professional",
            "duration": 30
        }
        
        result = tool.run(json.dumps(test_data))
        result_data = json.loads(result)
        
        print("Concept Generation Tool: ✅ PASSED")
        print(f"Generated concept: {result_data.get('concept', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"Concept Generation Tool: ❌ FAILED - {str(e)}")
        return False

def test_script_tool():
    """Test the script writing tool"""
    try:
        from agent.tools.script import ScriptWritingTool
        
        tool = ScriptWritingTool()
        
        test_data = {
            "concept": {"concept": "Revolutionary tech solution", "hook": "Transform your business"},
            "brand_info": {"brand_name": "TechFlow", "duration": 30}
        }
        
        result = tool.run(json.dumps(test_data))
        result_data = json.loads(result)
        
        print("Script Writing Tool: ✅ PASSED") 
        return True
        
    except Exception as e:
        print(f"Script Writing Tool: ❌ FAILED - {str(e)}")
        return False

def test_api_components():
    """Test API components"""
    try:
        from api.main import app, GenerateRequest
        
        # Test that we can create a request model
        request = GenerateRequest(
            brand_name="Test Brand",
            brand_description="Test description"
        )
        
        print("API Components: ✅ PASSED")
        print(f"Created request for: {request.brand_name}")
        return True
        
    except Exception as e:
        print(f"API Components: ❌ FAILED - {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing ReelForge Components\n")
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found. Some tests may fail.\n")
    
    tests = [
        test_api_components,
        test_concept_tool,
        test_script_tool
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ReelForge is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()