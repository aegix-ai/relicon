#!/usr/bin/env python3
"""
Test script for ReelForge API
"""
import sys
import os
sys.path.append('.')
from api.main import app

if __name__ == "__main__":
    import uvicorn
    print("Starting ReelForge API server...")
    print("Visit http://localhost:8000 to access the interface")
    print("API docs available at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")