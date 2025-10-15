# Next.js Project - Replit Configuration

## Overview
This is a Next.js 14 application using the App Router, TypeScript, and Tailwind CSS. The project was migrated from Vercel to Replit on October 15, 2025.

**Current Status:** Running successfully on Replit
**Framework:** Next.js 14.2.16
**Package Manager:** pnpm
**Runtime:** Node.js

## Recent Changes

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
│   │   └── waitlist/     # Waitlist signup API
│   ├── contact/           # Contact page
│   ├── dashboard/         # Dashboard section (requires login)
│   │   ├── ads/          # Ads archive page
│   │   ├── chat/         # AI assistant chat page
│   │   ├── studio/       # Creative studio page
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
├── hooks/                # Custom React hooks
├── lib/                  # Utility functions
├── public/               # Static assets
│   ├── images/          # Image files
│   ├── [ad images]      # 18 TikTok ad creative images
│   └── [various icons and placeholders]
├── styles/              # Additional styles
└── [config files]       # Next.js, TypeScript, Tailwind configs
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
- Campaign setup form with product details
- Target audience and creative style selection
- Live TikTok ad preview (9:16 format)
- Interactive preview with engagement metrics

**Navigation:**
- Collapsible sidebar (expands on hover on medium screens)
- Always expanded on large screens (1200px+)
- Settings and Profile modals
- Floating AI chat assistant on all dashboard pages

## Development

### Running the Project
- **Development server:** `pnpm run dev` (runs on port 5000)
- **Production build:** `pnpm run build`
- **Production server:** `pnpm run start`
- **Linting:** `pnpm run lint`

### Deployment
The project is configured for Replit's autoscale deployment:
- **Build command:** `pnpm run build`
- **Start command:** `pnpm start`
- Stateless website suitable for autoscaling

## Environment Variables
The following environment variables are automatically configured:
- `DATABASE_URL`: PostgreSQL connection string
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`: Database connection details

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

## User Preferences
No specific user preferences documented yet.

## Notes
- The project uses image optimization set to `unoptimized: true` in next.config.mjs
- ESLint and TypeScript errors are ignored during builds (configured in next.config.mjs)
- All dependencies are managed through pnpm
