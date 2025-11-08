import { NextRequest, NextResponse } from 'next/server'
import { supabaseServer } from '@/lib/supabase-server'

export async function POST(request: NextRequest) {
  try {
    const { user_email, message, message_type = 'general' } = await request.json()

    if (!user_email || !message) {
      return NextResponse.json({ error: 'Email and message required' }, { status: 400 })
    }

    const { data, error } = await supabaseServer
      .from('user_messages')
      .insert([{ user_email, message, message_type }])
      .select()

    if (error) throw error

    return NextResponse.json({ success: true, data })
  } catch (error) {
    return NextResponse.json({ error: 'Failed to save message' }, { status: 500 })
  }
}
