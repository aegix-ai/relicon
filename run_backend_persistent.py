#!/usr/bin/env python3
"""Run the Python FastAPI backend persistently"""
import os
import sys
import uvicorn
import signal
import time
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def signal_handler(signum, frame):
    print("Shutting down backend...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    print("Starting Relicon Python Backend...")
    
    # Set environment variables
    os.environ['PYTHONPATH'] = str(Path(__file__).parent)
    
    try:
        from main import app
        print("✓ FastAPI app loaded successfully")
        
        # Run the server
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            log_level="info",
            reload=False
        )
    except Exception as e:
        print(f"Failed to start backend: {e}")
        sys.exit(1)