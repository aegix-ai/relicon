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
- July 15, 2025: MAJOR ARCHITECTURAL REFACTOR - Central Highway Implementation
- UNIFIED MAIN.PY: Transformed main.py into the central highway of the entire application:
  - Integrated all video generation components (enhanced_video_generator, ai_planner, luma_service)
  - Unified AI planning systems (dynamic_tree_planner, energetic_script_generator)
  - Consolidated task management (tasks.py functions)
  - Created comprehensive API endpoints for all system capabilities
  - Added unified service initialization and health monitoring
  - Established single entry point for all system operations
- NEW API ENDPOINTS: Complete video generation and management system:
  - /generate-video - Main video generation endpoint with background processing
  - /generate-plan - AI planning using standard or tree planner
  - /generate-script - Energetic script generation
  - /execute-task - Task management for metrics and optimization
  - /video-status/{job_id} - Job status tracking
  - /download-video/{job_id} - Video file download
  - /luma-status/{job_id} - Luma AI job monitoring
  - /health - Comprehensive system health check
  - /system-info - Complete system capabilities overview
- ENHANCED SYSTEM ARCHITECTURE: Now truly unified with main.py as central orchestrator:
  - All video generation flows through main.py
  - All AI planning components accessible via single API
  - All task management centralized
  - All feedback loop functionality integrated
  - Single dependency chain for system visualization
- PRESERVED FUNCTIONALITY: All existing features maintained while creating unified interface
- PREVIOUS: UI POLISH & PLATFORM CLEANUP - Core Integration Focus
- PREVIOUS: AUTONOMOUS FEEDBACK LOOP SYSTEM - Complete Performance Optimization
- IMPLEMENTED: Nightly feedback loop system with comprehensive performance tracking:
  1. Automated metrics collection from Meta and TikTok APIs (02:00 UTC daily)
  2. Real-time revenue tracking via Shopify webhooks with HMAC verification
  3. ROAS calculation and automatic winner identification (top 25% performers)
  4. AI-powered next-generation hook generation using GPT-4o
  5. Complete database schema for metrics, sales, and ad performance tracking
- ENHANCED: AI Agent System with LangChain integration:
  - Analyzes winning ad patterns and psychological triggers
  - Generates 5 optimized hooks per ad with confidence scoring
  - Multi-platform optimization (Meta, TikTok, universal)
  - Pattern recognition for emotional triggers and conversion elements
- ADDED: Production-ready API endpoints:
  - /webhook/shopify for order tracking and conversion attribution
  - /next-gen/{ad_id} for AI-powered hook generation
  - /analytics/summary for performance dashboard data
  - Complete error handling and retry logic
- INTEGRATED: Celery task scheduling system:
  - Automated nightly processing with Redis broker
  - Fault-tolerant API calls with exponential backoff
  - Comprehensive logging and monitoring capabilities
- ESTABLISHED: Foundation for autonomous learning and continuous optimization
- PREPARED: Complete deployment configuration for Replit environment
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```