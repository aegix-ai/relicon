#!/usr/bin/env python3
"""Start the Python FastAPI backend server"""
import uvicorn
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

if __name__ == "__main__":
    from main import app
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")