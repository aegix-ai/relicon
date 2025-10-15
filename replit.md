# Next.js Project - Replit Configuration

## Overview
This is a Next.js 14 application using the App Router, TypeScript, and Tailwind CSS. The project was migrated from Vercel to Replit on October 15, 2025.

**Current Status:** Running successfully on Replit
**Framework:** Next.js 14.2.16
**Package Manager:** pnpm
**Runtime:** Node.js

## Recent Changes

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
│   ├── contact/           # Contact page
│   ├── join-waitlist/     # Waitlist page
│   ├── login/             # Login page
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── ui/               # Shadcn/ui components
│   ├── scroll-to-top.tsx
│   └── theme-provider.tsx
├── hooks/                # Custom React hooks
├── lib/                  # Utility functions
├── public/               # Static assets
│   ├── images/          # Image files
│   └── [various icons and placeholders]
├── styles/              # Additional styles
└── [config files]       # Next.js, TypeScript, Tailwind configs
```

### Key Technologies
- **Frontend:** React 18, Next.js 14 (App Router)
- **Styling:** Tailwind CSS with custom components
- **UI Components:** Radix UI primitives, Shadcn/ui
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
No environment variables are currently configured. If you need to add API keys or secrets:
1. Use Replit's Secrets management in the Tools panel
2. Access them in your code via `process.env.VARIABLE_NAME`

## User Preferences
No specific user preferences documented yet.

## Notes
- The project uses image optimization set to `unoptimized: true` in next.config.mjs
- ESLint and TypeScript errors are ignored during builds (configured in next.config.mjs)
- All dependencies are managed through pnpm
