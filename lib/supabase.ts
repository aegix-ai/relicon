import { createClient } from '@supabase/supabase-js'

// Supabase configuration
// Demo mode (NEXT_PUBLIC_RELICON_DEMO=1 or no Supabase env): a placeholder client so pages load without a cloud DB.
export const isDemo =
  process.env.NEXT_PUBLIC_RELICON_DEMO === '1' ||
  !process.env.NEXT_PUBLIC_SUPABASE_URL ||
  !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'http://localhost:54321'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'demo-mode-no-supabase'

// Create a single supabase client for interacting with your database
export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database types for type safety
export interface WaitlistSignup {
  id?: number
  name: string
  email: string
  company?: string | null
  monthly_ad_spend?: string | null
  primary_goal?: string | null
  created_at?: string
}

export interface ContactMessage {
  id?: number
  name: string
  email: string
  subject: string
  message: string
  status?: string
  created_at?: string
}
