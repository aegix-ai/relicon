import { createClient } from '@supabase/supabase-js'

// Supabase configuration
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

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
