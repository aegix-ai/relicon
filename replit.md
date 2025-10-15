# Next.js Project - Replit Configuration

## Overview
This is a Next.js 14 application using the App Router, TypeScript, and Tailwind CSS. The project was migrated from Vercel to Replit on October 15, 2025.

**Current Status:** Running successfully on Replit with AI Ad Generation Engine
**Framework:** Next.js 14.2.16
**Package Manager:** pnpm
**Runtime:** Node.js + Python 3.11

## Recent Changes

### October 15, 2025 - Codebase Cleanup & Optimization
- Cleaned up codebase from 1.6GB to 1.5GB by removing:
  - Duplicate engine code in attached_assets/
  - Unused placeholder images (6 files)
  - Build caches (.next/cache, __pycache__)
  - Reorganized images folder structure
- Verified system integrity: all features working correctly
- Updated documentation with proper README

### October 15, 2025 - AI Ad Generation Engine Integration
- Integrated FastAPI/LangChain ad generation engine with Creative Studio
- Removed engine's standalone frontend, kept only backend functionality
- **Engine Features:**
  - AI-powered ad generation using GPT-4o, LangChain
  - Video generation with Luma AI Ray 2 (Ray-3 not yet available via API)
  - Professional voiceover via ElevenLabs TTS
  - Background music generation
  - Cost-optimized 720p resolution (~$1.40 per 18-second video)
- **Creative Studio Integration:**
  - Form collects product details, audience, and creative style
  - Real-time progress tracking during ad generation
  - Generated ads display in TikTok 9:16 frame with pause/play controls
  - Preserves authentic TikTok UI overlay (likes, comments, share)
  - Video playback behind TikTok frame for realistic preview
- **API Architecture:**
  - FastAPI backend runs on port 8000
  - Next.js API routes proxy requests to engine
  - `/api/engine/generate` - Start ad generation
  - `/api/engine/status/{jobId}` - Poll generation progress
  - `/api/engine/health` - Engine health check
- **Workflows:**
  - Ad Engine: FastAPI server on port 8000
  - Dev Server: Next.js on port 5000

### October 15, 2025 - Logo Size Update
- Increased navbar and footer logos to 1.5x size
- Navbar logo: h-11 (44px) - was h-7 (28px)
- Footer logo: h-12 (48px) - was h-8 (32px)
- Updated across all pages: Landing, Login, Join Waitlist, About, Contact

### October 15, 2025 - Database & Authentication Implementation
- Created PostgreSQL database for waitlist signups with table schema:
  - Stores: name, email, company, monthly_ad_spend, primary_goal, created_at
  - Email uniqueness constraint to prevent duplicate signups
- Connected waitlist form to database via API route (`/api/waitlist`)
  - Form validates and saves all signups to database
  - Error handling for duplicate emails and server errors
  - Loading states and user feedback
- Implemented login authentication with specific credentials:
  - Valid email: team@getrelicon.com
  - Valid password: Relicon123456
  - Prevents unauthorized access to dashboard
- Updated all page logos to use `relicon-full-logo.png` (navbar and footer)

### October 15, 2025 - Dashboard Implementation
- Implemented complete Relicon advertising dashboard at `/dashboard`
- Created dashboard components:
  - MetricCard: Displays key metrics (ROAS, Conversions, Spend, CTR)
  - PerformanceChart: Interactive area chart with dual Y-axis
  - CampaignTable: Recent campaigns data table
  - AppSidebar: Collapsible navigation sidebar with logo
  - ChatPanel: Floating AI assistant chat interface
- Added dashboard pages:
  - Main Dashboard: Performance overview with metrics
  - Ads Archive: Searchable table of all ad creatives
  - Chat: Full-page AI assistant interface
  - Creative Studio: TikTok ad creation with live preview
- Implemented Settings and Profile modals
- Added 18 ad creative images to public folder
- Configured login page to redirect to `/dashboard` after sign-in
- Added scrollbar-hide utility to globals.css

### October 15, 2025 - Vercel to Replit Migration
- Configured Next.js to bind to port 5000 on 0.0.0.0 for Replit compatibility
- Updated package.json scripts:
  - `dev`: `next dev -p 5000 -H 0.0.0.0`
  - `start`: `next start -p 5000 -H 0.0.0.0`
- Installed all dependencies with pnpm
- Configured development workflow to run Next.js dev server
- Set up autoscale deployment configuration
- Updated .gitignore for Replit environment

## Project Architecture

### Directory Structure
```
├── app/                    # Next.js App Router pages
│   ├── about/             # About page
│   ├── api/               # API routes
│   │   ├── engine/       # Ad engine proxy routes
│   │   │   ├── generate/ # Start ad generation
│   │   │   ├── status/   # Check generation status
│   │   │   └── health/   # Engine health check
│   │   └── waitlist/     # Waitlist signup API
│   ├── contact/           # Contact page
│   ├── dashboard/         # Dashboard section (requires login)
│   │   ├── ads/          # Ads archive page
│   │   ├── chat/         # AI assistant chat page
│   │   ├── studio/       # Creative studio with ad generation
│   │   ├── layout.tsx    # Dashboard layout with sidebar
│   │   └── page.tsx      # Main dashboard
│   ├── join-waitlist/     # Waitlist page (saves to database)
│   ├── login/             # Login page (authenticated access)
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── chat/             # Chat panel component
│   ├── dashboard/        # Dashboard-specific components
│   ├── icons/            # Custom icon components
│   ├── layout/           # Layout components (AppSidebar)
│   ├── modals/           # Modal components
│   ├── ui/               # Shadcn/ui components
│   ├── scroll-to-top.tsx
│   └── theme-provider.tsx
├── engine/               # AI Ad Generation Backend
│   ├── backend/         # FastAPI application
│   │   ├── api/        # API endpoints
│   │   └── core/       # Job management
│   ├── core/           # Core services
│   │   ├── orchestrator.py      # Ad generation orchestration
│   │   ├── planning_service.py  # AI creative planning (GPT-4o)
│   │   ├── video_service.py     # Video generation (Hailuo/Luma)
│   │   ├── audio_service.py     # Voiceover (ElevenLabs)
│   │   ├── music_service.py     # Background music
│   │   ├── assembly_service.py  # Video assembly (FFmpeg)
│   │   ├── cost_tracker.py      # Cost optimization
│   │   └── logger.py            # Structured logging
│   ├── interfaces/      # Service interfaces
│   ├── providers/       # AI service providers
│   │   ├── openai.py   # OpenAI GPT-4o
│   │   ├── hailuo.py   # Hailuo-02 video generation
│   │   ├── luma.py     # Luma AI fallback
│   │   └── elevenlabs.py # ElevenLabs TTS/Music
│   ├── config/         # Configuration
│   ├── outputs/        # Generated videos
│   └── server.py       # FastAPI server entry point
├── hooks/              # Custom React hooks
├── lib/                # Utility functions
├── public/             # Static assets
│   ├── images/        # Image files
│   ├── [ad images]    # 18 TikTok ad creative images
│   └── [various icons and placeholders]
├── styles/            # Additional styles
└── [config files]     # Next.js, TypeScript, Tailwind configs
```

### Key Technologies
- **Frontend:** React 18, Next.js 14 (App Router)
- **Styling:** Tailwind CSS with custom components
- **UI Components:** Radix UI primitives, Shadcn/ui
- **Database:** PostgreSQL (Replit-managed)
- **Forms:** React Hook Form with Zod validation
- **Animation:** Framer Motion
- **Icons:** Lucide React
- **Type Safety:** TypeScript
- **Backend:** FastAPI, Python 3.11
- **AI/ML:** OpenAI GPT-4o, LangChain
- **Video:** Hailuo-02 (MiniMax), Luma AI
- **Audio:** ElevenLabs TTS & Music Generation

### Component Library
The project uses a comprehensive UI component library built on Radix UI:
- Form elements (Input, Checkbox, Select, etc.)
- Navigation (Menu, Dropdown, Tabs)
- Feedback (Toast, Dialog, Alert)
- Data display (Table, Card, Avatar)
- Layout (Resizable Panels, Scroll Area)

### Dashboard Features
The `/dashboard` route contains a complete advertising management system:

**Main Dashboard:**
- Performance chart with dual Y-axis (ROAS and Ads Performance)
- Metric cards showing key KPIs with percentage changes
- Recent campaigns table with impressions, clicks, CTR, and spend

**Ads Archive (`/dashboard/ads`):**
- Searchable and filterable table of ad creatives
- Thumbnail previews with campaign details
- Status badges (active, paused, completed)
- Sortable columns for all metrics

**Chat Interface (`/dashboard/chat`):**
- Full-page AI assistant for campaign planning
- Message history with timestamps
- File and image attachment buttons
- Shift+Enter for multiline input

**Creative Studio (`/dashboard/studio`):**
- **Campaign Setup Form:**
  - Product name and description
  - Campaign type selection
  - Target audience description
  - Creative style tuning (Bold, Minimal, Luxury, Playful)
- **AI Ad Generation:**
  - Connects to FastAPI backend engine
  - Real-time progress tracking with percentage
  - Step-by-step status updates
  - Generates 18-second TikTok ads (9:16 format, 720p)
- **Live TikTok Preview:**
  - Authentic TikTok UI frame with interactions
  - Generated video plays behind TikTok overlay
  - Tap/click to pause/play video
  - Shows likes, comments, share, bookmark counts
  - Displays brand name and product description
  - Sponsored tag and CTA button
- **Ad Generation Pipeline:**
  1. AI Planning (GPT-4o analyzes product & creates scenes)
  2. Video Generation (Luma AI Ray 3 primary, Hailuo-02 fallback)
  3. Voiceover (ElevenLabs professional TTS)
  4. Background Music (ElevenLabs music generation)
  5. Assembly (FFmpeg combines all elements)

**Navigation:**
- Collapsible sidebar (expands on hover on medium screens)
- Always expanded on large screens (1200px+)
- Settings and Profile modals
- Floating AI chat assistant on all dashboard pages

## Development

### Running the Project
- **Development server:** `pnpm run dev` (runs on port 5000)
- **Ad Engine:** Automatically runs on port 8000
- **Production build:** `pnpm run build`
- **Production server:** `pnpm run start`
- **Linting:** `pnpm run lint`

### Deployment
The project is configured for Replit's autoscale deployment:
- **Build command:** `pnpm run build`
- **Start command:** `pnpm start`
- Stateless website suitable for autoscaling

## Environment Variables
The following environment variables are required:
- **Database:**
  - `DATABASE_URL`: PostgreSQL connection string
  - `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`: Database connection details
- **AI Services (for Ad Generation):**
  - `OPENAI_API_KEY`: OpenAI GPT-4o for creative planning
  - `LUMA_API_KEY`: Luma AI Ray 3 for video generation (primary)
  - `ELEVENLABS_API_KEY`: ElevenLabs for voiceover and music

## Authentication
- **Login Credentials:**
  - Email: team@getrelicon.com
  - Password: Relicon123456
- Only these credentials grant access to the dashboard

## Database
The project uses PostgreSQL for data storage:
- **Waitlist Signups Table:** Stores all join waitlist form submissions
  - Fields: id, name, email, company, monthly_ad_spend, primary_goal, created_at
  - Email has unique constraint to prevent duplicate signups

## Ad Generation Engine
The AI ad generation engine creates professional TikTok ads:

### Architecture
- **Modern Ad Structure:** Hook → Problem/Solution → Resolution/CTA (3 scenes × 6 seconds)
- **Cost Optimized:** ~$1.40 per 18-second video at 720p resolution
- **AI-Powered:** GPT-4o for creative planning and scene generation
- **Multi-Provider:** Luma AI Ray 3 primary, Hailuo-02 fallback for reliability
- **Professional Audio:** ElevenLabs TTS + background music at 15% volume

### Generation Flow
1. User fills Creative Studio form (product, audience, style)
2. Next.js sends request to `/api/engine/generate`
3. FastAPI creates job and starts generation
4. Frontend polls `/api/engine/status/{jobId}` every 2 seconds
5. Progress updates shown with percentage and current step
6. Completed video displays in TikTok frame with playback controls

### Output
- **Format:** MP4, 9:16 aspect ratio (720p)
- **Duration:** 18 seconds (3 scenes × 6 seconds)
- **Audio:** Professional voiceover + background music
- **Cost:** ~12-16 videos per $20 budget

## User Preferences
No specific user preferences documented yet.

## Notes
- The project uses image optimization set to `unoptimized: true` in next.config.mjs
- ESLint and TypeScript errors are ignored during builds (configured in next.config.mjs)
- All dependencies are managed through pnpm
- Python dependencies are managed through uv in the engine directory
- The Ad Engine runs as a separate FastAPI process on port 8000
- Frontend and backend communicate via Next.js API routes
