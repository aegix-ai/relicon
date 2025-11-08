# Relicon - AI Advertising Director

<p align="center">
  <img src="public/images/relicon-website-screenshot02.png" alt="Relicon Website Preview" width="100%">
</p>

## 🎯 What is Relicon?

Relicon is an AI-powered advertising platform that generates professional video advertisements automatically. It combines multiple AI services (GPT-4o, Luma AI, ElevenLabs) to create compelling 15-18 second video ads optimized for TikTok and Instagram.

**Key Features:**
- 🎬 Automated video generation from text descriptions
- 🎙️ AI-powered voiceovers and background music
- 📊 Real-time progress tracking
- 💰 Cost-optimized at ~$1.50-2.00 per video
- 🎨 Multiple creative styles and campaign types
- 📱 9:16 aspect ratio (perfect for social media)

## 📋 Quick Start

### Prerequisites

- Node.js 18+ and pnpm
- Python 3.11+
- Supabase account (free tier works fine)
- API Keys from: OpenAI, Luma AI, ElevenLabs

### Installation (5-minute setup)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd relicon-full

# 2. Install dependencies
pnpm install

# 3. Set up environment variables
cp .env.local.template .env.local
# Edit .env.local and add your API keys (see API_KEYS_GUIDE.md)

# 4. Set up Supabase database
# Follow SUPABASE_SETUP.md (10 minutes)
# Or: Go to https://app.supabase.com, create project, run supabase-schema.sql

# 5. Install Python dependencies
cd engine
pip install -r requirements.txt
cd ..

# 6. Validate setup
node scripts/validate-setup.js

# 7. Start both servers (unified command)
pnpm full              # Starts both frontend and backend
# OR use the script directly:
./start.sh
```

### First Video

1. Visit http://localhost:5000/dashboard/studio
2. Enter product name and description
3. Click "Create Ad"
4. Wait 5-10 minutes for generation
5. Download your video!

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| **[API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)** | How to obtain all required API keys (OpenAI, Luma, ElevenLabs) |
| **[SUPABASE_SETUP.md](SUPABASE_SETUP.md)** | Database setup with step-by-step instructions |
| **[.env.local.template](.env.local.template)** | Environment variables template with explanations |

## 🏗️ Tech Stack

### Frontend
- **Next.js 14** (App Router) - React framework with SSR
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **Shadcn/ui** - 56+ pre-built components
- **Supabase JS** - Database client
- **Framer Motion** - Animations

### Backend
- **FastAPI** (Python 3.11) - High-performance API framework
- **Supabase** (PostgreSQL) - Database and storage
- **AI Services:**
  - **OpenAI GPT-4o** - Script and blueprint generation
  - **Luma AI Ray-2** - Video generation (720p, 9:16)
  - **ElevenLabs** - Voice synthesis and music

### Architecture
- Service-oriented backend with provider abstraction
- Real-time progress tracking via polling
- Cost-optimized video generation pipeline
- Database persistence for all generated content

## 📁 Project Structure

```
relicon-full/
├── app/                        # Next.js App Router
│   ├── dashboard/
│   │   ├── studio/            # 🎬 Creative Studio (main feature)
│   │   ├── ads/               # 📼 Generated ads archive
│   │   └── chat/              # 💬 AI assistant
│   ├── api/
│   │   ├── engine/            # Video generation API proxy
│   │   ├── waitlist/          # Waitlist form handler
│   │   ├── contact/           # Contact form handler
│   │   └── videos/            # Video listing API
│   ├── page.tsx               # Landing page
│   └── layout.tsx             # Root layout
│
├── components/
│   ├── ui/                    # 56+ Shadcn/ui components
│   ├── dashboard/             # Dashboard components
│   └── layout/                # Layout components (Sidebar, etc.)
│
├── engine/                     # Python AI Backend
│   ├── core/
│   │   ├── orchestrator.py    # Main video generation pipeline
│   │   ├── planning_service.py # GPT-4o blueprint generation
│   │   ├── video_service.py   # Video generation coordination
│   │   ├── audio_service.py   # Audio/voiceover generation
│   │   └── assembly_service.py # Video assembly with FFmpeg
│   ├── providers/
│   │   ├── openai.py          # OpenAI integration
│   │   ├── luma.py            # Luma AI video generation
│   │   ├── elevenlabs.py      # ElevenLabs audio
│   │   └── hailuo.py          # Fallback video provider
│   ├── config/
│   │   └── settings.py        # Centralized configuration
│   └── server.py              # FastAPI entry point
│
├── lib/
│   ├── supabase.ts            # Client-side Supabase
│   └── supabase-server.ts     # Server-side Supabase (RLS bypass)
│
├── scripts/
│   └── validate-setup.js      # ✅ Setup validation script
│
├── public/                     # Static assets
├── supabase-schema.sql        # 🗄️ Database schema
├── API_KEYS_GUIDE.md          # 🔑 API keys documentation
├── SUPABASE_SETUP.md          # 📖 Database setup guide
└── .env.local.template        # ⚙️ Environment template
```

## 🚀 Features

### Creative Studio
- Form-based campaign creation
- Real-time TikTok-style preview
- Progress tracking with status updates
- Multiple campaign types (awareness, conversion, engagement)
- Customizable creative styles

### 3-Scene Video Architecture
Each video follows a proven advertising formula:
1. **Hook** (5-6s) - Attention-grabbing opening
2. **Problem** (5-6s) - Pain point identification
3. **Solution** (5-6s) - Product presentation

### Database Features
- Automatic storage of all generated videos
- Job status tracking (queued, processing, completed, failed)
- Campaign metadata and analytics
- Waitlist and contact form submissions

## ⚙️ Configuration

### Environment Variables

```bash
# Database (Required)
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbG...
SUPABASE_SERVICE_ROLE_KEY=eyJhbG...

# AI Services (Required)
OPENAI_API_KEY=sk-...
LUMA_API_KEY=luma_...
ELEVENLABS_API_KEY=...

# Optional
HAILUO_API_KEY=...           # Backup video provider
ADMIN_API_KEY=...            # Admin endpoints
ENGINE_URL=http://localhost:8000
```

**See [.env.local.template](.env.local.template) for detailed explanations**

## 🧪 Testing Your Setup

Run the validation script to check everything:

```bash
node scripts/validate-setup.js
```

This will verify:
- ✅ Environment file exists
- ✅ All required variables are set
- ✅ Supabase connection works
- ✅ API keys are valid
- ✅ Backend is running

## 💰 Cost Breakdown

| Service | Cost per Video | Notes |
|---------|---------------|-------|
| OpenAI GPT-4o | $0.10-0.20 | Script generation |
| Luma AI | $1.20 | 3 clips × $0.40/5s at 720p |
| ElevenLabs | $0.05-0.10 | Voice + music (or free tier) |
| **Total** | **$1.50-2.00** | vs $500-2000 manual production |

**Savings**: 95-99% cost reduction vs traditional video production

## 🛠️ Development

### Start Development Servers

```bash
# Terminal 1 - Frontend
pnpm dev

# Terminal 2 - Backend
cd engine
python server.py

# Visit http://localhost:5000
```

### Useful Scripts

```bash
# Validate setup
node scripts/validate-setup.js

# Run linter
pnpm lint

# Build for production
pnpm build

# Start production server
pnpm start
```

### API Endpoints

**Frontend API Routes:**
- `POST /api/engine/generate` - Start video generation
- `GET /api/engine/status/[jobId]` - Get job status
- `GET /api/engine/video/[filename]` - Stream video
- `GET /api/videos` - List all generated videos
- `POST /api/waitlist` - Add to waitlist
- `POST /api/contact` - Submit contact form

**Backend API Endpoints:**
- `POST /generate` - Create generation job
- `GET /status/{job_id}` - Job status
- `GET /video/{filename}` - Serve video file
- `GET /health` - Health check

## 🔐 Security Notes

**Current State:**
- ⚠️ No authentication on dashboard (development mode)
- ✅ RLS enabled on Supabase tables
- ✅ API keys stored in environment variables
- ✅ CORS configured for same-origin

**Before Production:**
1. Implement Supabase Auth
2. Add authentication middleware
3. Restrict CORS to specific domains
4. Enable TypeScript strict mode
5. Add rate limiting
6. Use signed URLs for video access

## 🤝 Contributing

This is a private project. For issues or features:
1. Create an issue describing the problem/feature
2. Wait for approval before starting work
3. Follow existing code style and patterns

## 📄 License

Proprietary - All rights reserved

## 🆘 Support

---
