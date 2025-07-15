#!/usr/bin/env python3
"""
System health check script for Relicon AI Video Generation Platform
Validates all system components and dependencies
"""
import os
import subprocess
import requests
from pathlib import Path
from config.settings import settings
from core.database import db_manager
from external.apis import luma_client, openai_client

class ReliconSystemCheck:
    """System health check utility"""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
    
    def check_environment_variables(self):
        """Check required environment variables"""
        print("Checking environment variables...")
        
        required_vars = [
            "DATABASE_URL",
            "OPENAI_API_KEY"
        ]
        
        optional_vars = [
            "LUMA_API_KEY",
            "ELEVENLABS_API_KEY",
            "META_ACCESS_TOKEN",
            "TIKTOK_ACCESS_TOKEN",
            "SHOPIFY_WEBHOOK_SECRET"
        ]
        
        for var in required_vars:
            if os.getenv(var):
                print(f"✓ {var} is set")
                self.checks_passed += 1
            else:
                print(f"❌ {var} is missing (required)")
                self.checks_failed += 1
        
        for var in optional_vars:
            if os.getenv(var):
                print(f"✓ {var} is set")
            else:
                print(f"⚠ {var} is not set (optional)")
    
    def check_database_connection(self):
        """Check database connectivity"""
        print("\nChecking database connection...")
        
        try:
            db_manager.initialize()
            session = db_manager.get_session()
            
            # Try a simple query
            result = session.execute("SELECT 1").fetchone()
            if result:
                print("✓ Database connection successful")
                self.checks_passed += 1
            else:
                print("❌ Database query failed")
                self.checks_failed += 1
                
            session.close()
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            self.checks_failed += 1
    
    def check_external_apis(self):
        """Check external API connections"""
        print("\nChecking external APIs...")
        
        # Check OpenAI API
        try:
            if settings.OPENAI_API_KEY:
                result = openai_client.generate_text("Hello", max_tokens=5)
                if result:
                    print("✓ OpenAI API connection successful")
                    self.checks_passed += 1
                else:
                    print("❌ OpenAI API call failed")
                    self.checks_failed += 1
            else:
                print("⚠ OpenAI API key not set")
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            self.checks_failed += 1
        
        # Check Luma API
        try:
            if settings.LUMA_API_KEY:
                account_info = luma_client.get_account_info()
                if not account_info.get("error"):
                    print("✓ Luma API connection successful")
                    self.checks_passed += 1
                else:
                    print(f"❌ Luma API error: {account_info.get('error')}")
                    self.checks_failed += 1
            else:
                print("⚠ Luma API key not set")
        except Exception as e:
            print(f"❌ Luma API error: {e}")
            self.checks_failed += 1
    
    def check_ffmpeg(self):
        """Check FFmpeg installation"""
        print("\nChecking FFmpeg...")
        
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"✓ FFmpeg found: {version_line}")
                self.checks_passed += 1
            else:
                print("❌ FFmpeg not working properly")
                self.checks_failed += 1
                
        except subprocess.TimeoutExpired:
            print("❌ FFmpeg command timed out")
            self.checks_failed += 1
        except FileNotFoundError:
            print("❌ FFmpeg not found - please install FFmpeg")
            self.checks_failed += 1
        except Exception as e:
            print(f"❌ FFmpeg check failed: {e}")
            self.checks_failed += 1
    
    def check_directories(self):
        """Check required directories"""
        print("\nChecking directories...")
        
        required_dirs = [
            settings.TEMP_DIR,
            settings.OUTPUT_DIR,
            settings.ASSETS_DIR
        ]
        
        for directory in required_dirs:
            if directory.exists():
                if os.access(directory, os.W_OK):
                    print(f"✓ {directory} exists and is writable")
                    self.checks_passed += 1
                else:
                    print(f"❌ {directory} exists but is not writable")
                    self.checks_failed += 1
            else:
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                    print(f"✓ Created directory: {directory}")
                    self.checks_passed += 1
                except Exception as e:
                    print(f"❌ Could not create directory {directory}: {e}")
                    self.checks_failed += 1
    
    def check_api_server(self):
        """Check if API server is running"""
        print("\nChecking API server...")
        
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print("✓ API server is running and healthy")
                    self.checks_passed += 1
                else:
                    print("❌ API server is not healthy")
                    self.checks_failed += 1
            else:
                print(f"❌ API server returned status {response.status_code}")
                self.checks_failed += 1
                
        except requests.exceptions.ConnectionError:
            print("❌ API server is not running (connection refused)")
            self.checks_failed += 1
        except requests.exceptions.Timeout:
            print("❌ API server is not responding (timeout)")
            self.checks_failed += 1
        except Exception as e:
            print(f"❌ API server check failed: {e}")
            self.checks_failed += 1
    
    def check_python_packages(self):
        """Check required Python packages"""
        print("\nChecking Python packages...")
        
        required_packages = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "openai",
            "requests",
            "pydantic"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✓ {package} is installed")
                self.checks_passed += 1
            except ImportError:
                print(f"❌ {package} is not installed")
                self.checks_failed += 1
    
    def run_full_check(self):
        """Run complete system check"""
        print("Starting Relicon system health check...")
        print("=" * 60)
        
        self.check_environment_variables()
        self.check_python_packages()
        self.check_database_connection()
        self.check_external_apis()
        self.check_ffmpeg()
        self.check_directories()
        self.check_api_server()
        
        print("\n" + "=" * 60)
        print(f"Health check completed:")
        print(f"✅ Passed: {self.checks_passed}")
        print(f"❌ Failed: {self.checks_failed}")
        
        if self.checks_failed == 0:
            print("\n🎉 All checks passed! System is ready.")
            return True
        else:
            print(f"\n⚠ {self.checks_failed} checks failed. Please resolve issues before using the system.")
            return False

if __name__ == "__main__":
    checker = ReliconSystemCheck()
    success = checker.run_full_check()
    exit(0 if success else 1)