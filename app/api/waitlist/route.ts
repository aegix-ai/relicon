import { NextRequest, NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';
import { supabaseServer } from '@/lib/supabase-server';
import type { WaitlistSignup } from '@/lib/supabase';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, email, company, monthlyAdSpend, primaryGoal } = body;

    // Validate required fields
    if (!name || !email) {
      return NextResponse.json(
        { error: 'Name and email are required' },
        { status: 400 }
      );
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: 'Invalid email format' },
        { status: 400 }
      );
    }

    // Prepare data for insertion
    const signupData: Omit<WaitlistSignup, 'id' | 'created_at'> = {
      name: name.trim(),
      email: email.toLowerCase().trim(),
      company: company?.trim() || null,
      monthly_ad_spend: monthlyAdSpend || null,
      primary_goal: primaryGoal || null,
    };

    // Insert into Supabase using server client (bypasses RLS)
    const { data, error } = await supabaseServer
      .from('waitlist_signups')
      .insert([signupData])
      .select()
      .single();

    if (error) {
      console.error('Supabase error:', error);

      // Handle duplicate email error
      if (error.code === '23505' || error.message.includes('duplicate')) {
        return NextResponse.json(
          { error: 'This email is already on the waitlist' },
          { status: 409 }
        );
      }

      return NextResponse.json(
        { error: 'Failed to save signup', details: error.message },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      data: data,
      message: 'Successfully added to waitlist!',
    });
  } catch (error: any) {
    console.error('Error saving waitlist signup:', error);

    return NextResponse.json(
      { error: 'Failed to save signup', details: error.message },
      { status: 500 }
    );
  }
}

// Optional: GET endpoint to retrieve waitlist count (for admin purposes)
export async function GET(request: NextRequest) {
  try {
    // Check for admin authorization (you should implement proper auth)
    const authHeader = request.headers.get('authorization');
    if (authHeader !== `Bearer ${process.env.ADMIN_API_KEY}`) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const { count, error } = await supabaseServer
      .from('waitlist_signups')
      .select('*', { count: 'exact', head: true });

    if (error) {
      throw error;
    }

    return NextResponse.json({
      success: true,
      count: count || 0,
    });
  } catch (error: any) {
    console.error('Error fetching waitlist count:', error);

    return NextResponse.json(
      { error: 'Failed to fetch waitlist count' },
      { status: 500 }
    );
  }
}
