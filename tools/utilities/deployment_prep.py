#!/usr/bin/env python3
"""
Deployment preparation script for Relicon AI Video Generation Platform
Prepares system for production deployment
"""
import os
import json
import shutil
import subprocess
from pathlib import Path
from config.settings import settings

class DeploymentPrep:
    """Prepares system for deployment"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.build_dir = Path("build")
        self.dist_dir = Path("dist")
    
    def clean_build_directories(self):
        """Clean previous build directories"""
        print("Cleaning build directories...")
        
        for directory in [self.build_dir, self.dist_dir]:
            if directory.exists():
                shutil.rmtree(directory)
                print(f"✓ Removed {directory}")
        
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
    
    def copy_source_files(self):
        """Copy source files to build directory"""
        print("Copying source files...")
        
        # Core application files
        core_files = [
            "main.py",
            "config/",
            "core/",
            "ai/",
            "video/",
            "external/",
            "tasks/"
        ]
        
        for item in core_files:
            src = Path(item)
            if src.exists():
                dst = self.build_dir / item
                if src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                print(f"✓ Copied {item}")
    
    def create_requirements_file(self):
        """Create requirements.txt for Python dependencies"""
        print("Creating requirements.txt...")
        
        requirements = [
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0",
            "sqlalchemy>=2.0.0",
            "psycopg2-binary>=2.9.0",
            "openai>=1.0.0",
            "requests>=2.31.0",
            "pydantic>=2.0.0",
            "python-multipart>=0.0.6",
            "python-dotenv>=1.0.0"
        ]
        
        req_file = self.build_dir / "requirements.txt"
        with open(req_file, 'w') as f:
            f.write('\n'.join(requirements))
        
        print(f"✓ Created {req_file}")
    
    def create_dockerfile(self):
        """Create Dockerfile for containerization"""
        print("Creating Dockerfile...")
        
        dockerfile_content = '''FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    ffmpeg \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/assets /app/outputs /app/temp

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        
        dockerfile = self.build_dir / "Dockerfile"
        with open(dockerfile, 'w') as f:
            f.write(dockerfile_content)
        
        print(f"✓ Created {dockerfile}")
    
    def create_docker_compose(self):
        """Create docker-compose.yml for multi-service deployment"""
        print("Creating docker-compose.yml...")
        
        compose_content = '''version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LUMA_API_KEY=${LUMA_API_KEY}
      - ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
    volumes:
      - ./outputs:/app/outputs
      - ./assets:/app/assets
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=relicon
      - POSTGRES_USER=relicon
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7
    restart: unless-stopped

volumes:
  postgres_data:
'''
        
        compose_file = self.build_dir / "docker-compose.yml"
        with open(compose_file, 'w') as f:
            f.write(compose_content)
        
        print(f"✓ Created {compose_file}")
    
    def create_environment_template(self):
        """Create .env template for deployment"""
        print("Creating .env template...")
        
        env_template = '''# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/relicon

# AI Service API Keys
OPENAI_API_KEY=your_openai_api_key_here
LUMA_API_KEY=your_luma_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Platform Integration
META_ACCESS_TOKEN=your_meta_access_token_here
TIKTOK_ACCESS_TOKEN=your_tiktok_access_token_here
SHOPIFY_WEBHOOK_SECRET=your_shopify_webhook_secret_here

# System Configuration
DEBUG=false
VIDEO_QUALITY=1080p
DEFAULT_VIDEO_DURATION=30
MAX_VIDEO_DURATION=60
'''
        
        env_file = self.build_dir / ".env.template"
        with open(env_file, 'w') as f:
            f.write(env_template)
        
        print(f"✓ Created {env_file}")
    
    def create_deployment_guide(self):
        """Create deployment guide"""
        print("Creating deployment guide...")
        
        guide_content = '''# Relicon AI Video Generation Platform - Deployment Guide

## Quick Start

1. **Set up environment variables**:
   ```bash
   cp .env.template .env
   # Edit .env with your actual values
   ```

2. **Deploy with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **Verify deployment**:
   ```bash
   curl http://localhost:8000/health
   ```

## Production Deployment

### Requirements
- Docker and Docker Compose
- PostgreSQL database
- Redis instance
- External API keys (OpenAI, Luma AI, etc.)

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: Required for AI functionality
- `LUMA_API_KEY`: Required for video generation
- `ELEVENLABS_API_KEY`: Optional for voice synthesis
- `META_ACCESS_TOKEN`: Required for Meta integration
- `TIKTOK_ACCESS_TOKEN`: Required for TikTok integration
- `SHOPIFY_WEBHOOK_SECRET`: Required for Shopify integration

### Health Checks
The application provides a health check endpoint at `/health`.

### Monitoring
- Application logs are available via `docker-compose logs app`
- Database logs are available via `docker-compose logs db`

### Backup
Regular database backups are recommended using `pg_dump`.

### Scaling
For high traffic, consider:
- Multiple app instances behind a load balancer
- Separate database server
- Redis cluster for caching
- CDN for static assets

## API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `POST /api/generate-video` - Generate video
- `POST /api/generate-simple-video` - Generate simple video
- `POST /api/generate-hooks` - Generate hooks
- `POST /api/collect-metrics` - Collect metrics
- `POST /api/evaluate-creatives` - Evaluate creatives

### Webhook Endpoints
- `POST /webhooks/shopify` - Shopify webhook
- `POST /webhooks/meta` - Meta webhook
- `POST /webhooks/tiktok` - TikTok webhook

## Support
For issues and questions, refer to the main documentation.
'''
        
        guide_file = self.build_dir / "DEPLOYMENT.md"
        with open(guide_file, 'w') as f:
            f.write(guide_content)
        
        print(f"✓ Created {guide_file}")
    
    def run_deployment_prep(self):
        """Run complete deployment preparation"""
        print("Starting deployment preparation...")
        print("-" * 50)
        
        try:
            self.clean_build_directories()
            self.copy_source_files()
            self.create_requirements_file()
            self.create_dockerfile()
            self.create_docker_compose()
            self.create_environment_template()
            self.create_deployment_guide()
            
            print("-" * 50)
            print("✅ Deployment preparation completed successfully!")
            print(f"Build files are ready in: {self.build_dir}")
            print("\nNext steps:")
            print("1. Copy build files to your deployment server")
            print("2. Set up environment variables")
            print("3. Run: docker-compose up -d")
            
            return True
            
        except Exception as e:
            print(f"❌ Deployment preparation failed: {e}")
            return False

if __name__ == "__main__":
    prep = DeploymentPrep()
    prep.run_deployment_prep()