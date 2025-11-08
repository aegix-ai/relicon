import { NextRequest, NextResponse } from 'next/server';
import { supabaseServer } from '@/lib/supabase-server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(
  request: NextRequest,
  { params }: { params: { jobId: string } }
) {
  try {
    const engineUrl = process.env.ENGINE_URL || 'http://localhost:8000';
    
    // Add cache-busting to prevent stale responses
    const response = await fetch(`${engineUrl}/status/${params.jobId}?t=${Date.now()}`, {
      cache: 'no-store',
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json({ error: error.detail || 'Status check failed' }, { status: response.status });
    }

    const data = await response.json();

    console.log('Status from engine:', JSON.stringify(data, null, 2));

    // Update database with current job status
    let videoId = null;
    try {
      const updateData: any = {
        status: data.status,
        progress: data.progress || 0,
      };

      // Add video URL if completed
      if (data.status === 'completed' && data.video_url) {
        updateData.video_url = data.video_url;
        updateData.completed_at = new Date().toISOString();
      }

      // Add error message if failed
      if (data.status === 'failed' && data.message) {
        updateData.error_message = data.message;
      }

      const { data: videoRecord, error: dbError } = await supabaseServer
        .from('generated_videos')
        .update(updateData)
        .eq('job_id', params.jobId)
        .select('id')
        .single();

      if (dbError) {
        console.error('Database update error:', dbError);
        // Don't fail the request if database update fails
      } else if (videoRecord) {
        videoId = videoRecord.id;
      }
    } catch (dbError) {
      console.error('Database error:', dbError);
      // Don't fail the request if database operations fail
    }

    // Add video_id to response
    const responseData = {
      ...data,
      video_id: videoId
    };

    console.log('Sending to frontend:', JSON.stringify(responseData, null, 2));

    // Return with no-cache headers
    return NextResponse.json(responseData, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    });
  } catch (error) {
    console.error('Engine status API error:', error);
    return NextResponse.json(
      { error: 'Failed to get job status' },
      { status: 500 }
    );
  }
}
