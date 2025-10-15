import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const response = await fetch('http://localhost:8000/health');

    if (!response.ok) {
      return NextResponse.json({ error: 'Engine not available' }, { status: 503 });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Engine health check error:', error);
    return NextResponse.json(
      { error: 'Ad generation engine is offline' },
      { status: 503 }
    );
  }
}
