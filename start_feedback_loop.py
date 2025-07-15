#!/usr/bin/env python3
"""
Start script for Relicon feedback loop system.
This script initializes the database and starts the FastAPI server.
"""
import os
import sys
import uvicorn
from database import init_db

def main():
    """Initialize database and start server."""
    print("🚀 Starting Relicon Feedback Loop System...")
    
    # Initialize database
    print("📊 Initializing database...")
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    # Start FastAPI server
    print("🌐 Starting FastAPI server...")
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=3000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()