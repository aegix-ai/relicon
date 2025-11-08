import { NextRequest, NextResponse } from 'next/server';
import { supabaseServer } from '@/lib/supabase-server';
import {
  rateLimit,
  rateLimitResponse,
  validateJsonBody,
  sanitizeInput,
  isValidUrl,
  secureJsonResponse
} from '@/lib/api-security';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    // Rate limiting: 5 generation requests per hour per IP
    const rateLimitResult = rateLimit(request, 5, 3600000); // 1 hour
    if (!rateLimitResult.allowed) {
      return rateLimitResponse(rateLimitResult.resetTime);
    }

    const body = await request.json();

    // Validate required fields
    const validation = validateJsonBody(body, [
      'brand_name',
      'product_name',
      'product_description'
    ]);

    if (!validation.valid) {
      return secureJsonResponse({ error: validation.error }, 400);
    }

    // Sanitize string inputs
    body.brand_name = sanitizeInput(body.brand_name);
    body.brand_description = sanitizeInput(body.brand_description || '');
    body.product_name = sanitizeInput(body.product_name);
    body.product_description = sanitizeInput(body.product_description);
    body.target_audience = sanitizeInput(body.target_audience || '');
    body.creative_style = sanitizeInput(body.creative_style || '');
    body.call_to_action = sanitizeInput(body.call_to_action || '');

    // Validate product_image_url if provided
    if (body.product_image_url && !isValidUrl(body.product_image_url)) {
      return secureJsonResponse({
        error: 'Invalid product image URL'
      }, 400);
    }

    // Validate duration is reasonable
    if (body.duration && (body.duration < 10 || body.duration > 30)) {
      return secureJsonResponse({
        error: 'Duration must be between 10 and 30 seconds'
      }, 400);
    }

    // Forward to FastAPI engine
    const engineUrl = process.env.ENGINE_URL || 'http://localhost:8000';
    const response = await fetch(`${engineUrl}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json({ error: error.detail || 'Generation failed' }, { status: response.status });
    }

    const data = await response.json();

    // Store video generation job in database
    try {
      const { error: dbError } = await supabaseServer
        .from('generated_videos')
        .insert([{
          job_id: data.job_id,
          product_name: body.product_name || 'Untitled',
          product_description: body.product_description,
          campaign_type: body.campaign_type,
          target_audience: body.target_audience,
          creative_style: body.creative_style,
          product_image_url: body.product_image_url,
          status: 'queued',
          progress: 0,
          metadata: {
            brand_name: body.brand_name,
            brand_description: body.brand_description,
            tone: body.tone,
            duration: body.duration,
            call_to_action: body.call_to_action,
          }
        }]);

      if (dbError) {
        console.error('Database insert error:', dbError);
        // Don't fail the request if database insert fails
      }
    } catch (dbError) {
      console.error('Database error:', dbError);
      // Don't fail the request if database operations fail
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Engine API error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to ad generation engine' },
      { status: 500 }
    );
  }
}
