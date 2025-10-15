import { NextRequest, NextResponse } from 'next/server';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, email, company, monthlyAdSpend, primaryGoal } = body;

    if (!name || !email) {
      return NextResponse.json(
        { error: 'Name and email are required' },
        { status: 400 }
      );
    }

    const result = await pool.query(
      `INSERT INTO waitlist_signups (name, email, company, monthly_ad_spend, primary_goal) 
       VALUES ($1, $2, $3, $4, $5) 
       RETURNING *`,
      [name, email, company || null, monthlyAdSpend || null, primaryGoal || null]
    );

    return NextResponse.json({
      success: true,
      data: result.rows[0],
    });
  } catch (error: any) {
    console.error('Error saving waitlist signup:', error);
    
    if (error.code === '23505') {
      return NextResponse.json(
        { error: 'This email is already on the waitlist' },
        { status: 409 }
      );
    }

    return NextResponse.json(
      { error: 'Failed to save signup' },
      { status: 500 }
    );
  }
}
