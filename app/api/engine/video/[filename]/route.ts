import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(
  request: NextRequest,
  { params }: { params: { filename: string } }
) {
  try {
    const engineUrl = process.env.ENGINE_URL || 'http://localhost:8000';
    
    // Stream video directly without buffering to avoid cache issues
    const response = await fetch(`${engineUrl}/video/${params.filename}`, {
      cache: 'no-store' // Prevent Next.js from caching
    });

    if (!response.ok) {
      return NextResponse.json({ error: 'Video not found' }, { status: 404 });
    }

    // Stream the response directly without loading into memory
    return new NextResponse(response.body, {
      status: response.status,
      headers: {
        'Content-Type': 'video/mp4',
        'Content-Length': response.headers.get('Content-Length') || '',
        'Accept-Ranges': 'bytes',
        'Cache-Control': 'no-cache, no-store, must-revalidate', // Disable all caching
        'Pragma': 'no-cache',
        'Expires': '0'
      },
    });
  } catch (error) {
    console.error('Video proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to retrieve video' },
      { status: 500 }
    );
  }
}
