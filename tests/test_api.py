"""
API endpoint tests for Relicon AI Video Generation Platform
Tests all main API endpoints and functionality
"""
import pytest
import requests
import json
from typing import Dict, Any

class TestReliconAPI:
    """Test suite for Relicon API endpoints"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.headers = {"Content-Type": "application/json"}
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health check passed")
    
    def test_video_generation(self):
        """Test video generation endpoint"""
        payload = {
            "brand_name": "Test Brand",
            "brand_description": "Amazing test product for video generation",
            "duration": 15,
            "platform": "universal"
        }
        
        response = requests.post(
            f"{self.base_url}/api/generate-simple-video",
            json=payload,
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "video_url" in data
        print("✓ Video generation test passed")
    
    def test_stats_endpoint(self):
        """Test stats endpoint"""
        response = requests.get(f"{self.base_url}/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "ads" in data
        assert "sales" in data
        assert "winners" in data
        print("✓ Stats endpoint test passed")
    
    def test_metrics_collection(self):
        """Test metrics collection endpoint"""
        payload = {
            "platform": "meta",
            "ad_ids": ["123", "456"],
            "date_range": 7
        }
        
        response = requests.post(
            f"{self.base_url}/api/collect-metrics",
            json=payload,
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "platform" in data
        print("✓ Metrics collection test passed")
    
    def test_creative_evaluation(self):
        """Test creative evaluation endpoint"""
        payload = {
            "days": 30,
            "platform": "meta"
        }
        
        response = requests.post(
            f"{self.base_url}/api/evaluate-creatives",
            json=payload,
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_ads" in data
        assert "winners" in data
        print("✓ Creative evaluation test passed")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("Running Relicon API tests...")
        
        try:
            self.test_health_check()
            self.test_video_generation()
            self.test_stats_endpoint()
            self.test_metrics_collection()
            self.test_creative_evaluation()
            
            print("\n✅ All API tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            return False

if __name__ == "__main__":
    tester = TestReliconAPI()
    tester.run_all_tests()