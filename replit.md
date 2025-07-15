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
- July 2, 2025: ULTRA-DYNAMIC TREE PLANNER & ENERGETIC AUDIO SYSTEM - Revolutionary Enhancements
- IMPLEMENTED: Ultra-Dynamic Tree Planner with complete context awareness:
  1. Strategic Overview (CMO-level thinking)
  2. Campaign Architecture (Creative Director planning)
  3. Creative Components (Scene Designer crafting)
  4. Execution Details (Technical Director optimizing)
  5. Final Optimization (AI Director balancing everything)
- RESOLVED: Critical $8 cost issue - reduced to $2.42-4.80 per video via smart segment limits
- ENHANCED: Revolutionary energetic audio system:
  - Charismatic advertisement-style voiceover generation
  - Hook questions: "Have you ever...?", "Ready to discover...?"
  - +10dB volume boost with professional compression
  - High-quality TTS (tts-1-hd, alloy voice, 1.1x speed)
  - Chunked audio generation maintaining voice continuity
- EXPANDED: Multi-component optimization system:
  - Video: Luma AI prompts with camera movements and composition
  - Audio: Energetic delivery optimization maintaining volume/energy
  - Music: Background music style and tempo matching
  - Images: Thumbnail and key frame generation guidance
- TRANSFORMED: Audio quality from dry AI reading to professional TV commercial style
- OPTIMIZED: Complete context awareness prevents AI from forgetting previous planning steps
- PREPARED: Foundation for autonomous learning system with A/B test data integration
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```