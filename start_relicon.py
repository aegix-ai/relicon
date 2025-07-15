#!/usr/bin/env python3
"""
Relicon Startup Script
"""
import subprocess
import sys
import os

def main():
    # Change to the correct directory
    os.chdir('/home/runner/workspace')
    
    # Start the ReelForge server
    print("🚀 Starting ReelForge AI Video Generation Platform...")
    
    try:
        # Start the Python server
        subprocess.run([sys.executable, 'simple_server.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 ReelForge server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()