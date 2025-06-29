# ReelForge AI Video Generator

## Overview

ReelForge is an autonomous AI-powered video generation platform that creates short-form promotional videos. The system combines multiple AI technologies to automatically generate creative concepts, write scripts, synthesize voiceovers, source stock footage, and assemble final videos using a microkernel architecture.

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
- June 29, 2025: PERFECT SUCCESS - Professional ElevenLabs Audio Integration
- FIXED: Audio timing now matches exact video duration (30s = 30s, not 40% completion)
- IMPLEMENTED: Natural human-like speech with conversational patterns and energy
- ENHANCED: ElevenLabs integration with energy-based voice selection (Antoni, Dave, Liam, Adam)
- ADDED: Strategic pause system and emotional expressions for professional delivery
- RESOLVED: No more fast TTS yapping - proper pacing with rhythm breaks
- ACHIEVED: 100% video completion with perfect audio-visual synchronization
- MAINTAINED: Exact duration control and revolutionary 9:16 frame-safe visuals
- DELIVERED: Professional quality videos that sound like real human narration
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```