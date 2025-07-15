# Relicon AI Video Generator

## Overview

Relicon is an autonomous AI-powered video generation platform that creates short-form promotional videos. The system combines multiple AI technologies to automatically generate creative concepts, write scripts, synthesize voiceovers, source stock footage, and assemble final videos using a microkernel architecture.

## System Architecture

### Frontend Architecture
- **Framework**: React with TypeScript
- **UI Library**: Radix UI with shadcn/ui components
- **Styling**: Tailwind CSS with custom CSS variables
- **State Management**: TanStack React Query for API state
- **Routing**: Wouter for client-side routing
- **Build Tool**: Vite with React plugin

### Backend Architecture
- **API Framework**: FastAPI (Python) for REST endpoints
- **Database**: PostgreSQL with Drizzle ORM
- **Task Queue**: Celery with Redis as broker
- **AI Orchestration**: LangChain with OpenAI GPT-4o
- **Session Management**: Express.js with TypeScript for additional backend services

### Microkernel Pattern
The system follows a microkernel architecture where:
- **Kernel**: FastAPI application handles core API functionality
- **Plugins**: Individual AI tools (concept generation, script writing, TTS, etc.) that can be loaded dynamically
- **Agent**: LangChain-powered orchestrator that coordinates all tools

## Key Components

### AI Agent System (`agent/`)
- **Core Orchestrator**: LangChain agent that manages the entire video generation pipeline
- **Modular Tools**: Individual AI capabilities implemented as separate tools
  - Concept generation for creative ideas
  - Script writing for voiceover content
  - Timeline planning for video assembly
  - Text-to-speech for audio generation
  - Stock footage sourcing
  - FFmpeg video compilation

### API Layer (`api/`)
- **Main Application**: FastAPI server with job management
- **Schema Definitions**: Pydantic models for request/response validation
- **Dependency Injection**: Redis clients and shared resources

### Worker System (`workers/`)
- **Celery Tasks**: Asynchronous processing for video generation jobs
- **Job Status Tracking**: Redis-based progress monitoring
- **Error Handling**: Retry logic and failure recovery

### Frontend Application (`client/`)
- **Main Interface**: React-based form for video generation requests
- **Real-time Updates**: Job status polling and progress tracking
- **Component Library**: Comprehensive UI components using Radix primitives

## Data Flow

1. **Request Initiation**: User submits brand information through React frontend
2. **API Processing**: FastAPI receives request and creates job in Redis
3. **Task Queuing**: Celery worker picks up job for processing
4. **AI Pipeline**: LangChain agent orchestrates sequential tool execution:
   - Generate creative concept based on brand info
   - Write script segments with timing
   - Create detailed timeline with transitions
   - Generate voiceover audio files
   - Source and download stock footage
   - Compile final video with FFmpeg
5. **Progress Updates**: Job status updated in Redis throughout process
6. **Result Delivery**: Final video URL provided to frontend

## External Dependencies

### AI Services
- **OpenAI GPT-4o**: Primary language model for content generation
- **OpenAI TTS**: Text-to-speech synthesis (with ElevenLabs as alternative)
- **Pexels API**: Stock footage and imagery sourcing

### Infrastructure
- **PostgreSQL**: Primary database with Neon serverless option
- **Redis**: Job queue broker and result backend
- **FFmpeg**: Video processing and assembly

### Development Tools
- **Drizzle Kit**: Database schema management and migrations
- **ESBuild**: Server bundling for production
- **Replit Integration**: Development environment integration

## Deployment Strategy

### Development Environment
- **Vite Dev Server**: Hot reload for frontend development
- **Express Server**: TypeScript backend with middleware
- **Local Storage**: File system for assets during development

### Production Deployment
- **Containerization**: Docker support with multi-service compose
- **Static Assets**: Vite builds optimized frontend bundle
- **Process Management**: Separate processes for API and workers
- **Environment Variables**: Configuration through environment settings

### Storage Options
- **Local Storage**: Default for development
- **AWS S3**: Production asset storage
- **Database**: PostgreSQL for persistent data

## Recent Changes

```
Changelog:
- July 15, 2025: PROJECT STRUCTURE CLEANUP - Organized Core Architecture
- CLEAN STRUCTURE: Reorganized project into logical, maintainable structure:
  - frontend/ - Complete React frontend with Next.js integration
  - client/ - Core client-side application files
  - server/ - Backend Express.js server with TypeScript
  - shared/ - Shared schemas and types between frontend/backend
  - Core AI engine files in root directory for direct access
- REMOVED UNNECESSARY FILES: Eliminated testing, debugging, and demo files:
  - Deleted all test_*.py, debug_*.py, demo_*.py files
  - Removed output videos and temporary files
  - Cleaned up duplicate configurations and backups
  - Preserved only essential core functionality
- CORE AI ENGINE (Root Directory):
  - main.py - Central FastAPI application highway
  - enhanced_video_generator.py - Complete video generation pipeline
  - ai_planner.py - Intelligent video planning system
  - luma_service.py - Luma AI integration service
  - dynamic_tree_planner.py - Advanced tree-based planning
  - energetic_script_generator.py - Advertisement-style script creation
  - database.py - PostgreSQL database layer
  - agent.py - AI agent for hook generation
  - tasks.py - Task management system
- MAINTAINED FUNCTIONALITY: All core features preserved:
  - Complete video generation pipeline working
  - AI planning and script generation intact
  - Database operations and feedback loops operational
  - Frontend interface properly connected to backend
- PREVIOUS: MAJOR ARCHITECTURAL REFACTOR - Central Highway Implementation
- PREVIOUS: AUTONOMOUS FEEDBACK LOOP SYSTEM - Complete Performance Optimization
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```