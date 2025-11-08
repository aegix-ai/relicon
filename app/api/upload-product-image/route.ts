import { NextRequest, NextResponse } from 'next/server';
import { supabaseServer } from '@/lib/supabase-server';
import {
  rateLimit,
  rateLimitResponse,
  validateFileUpload,
  sanitizeInput,
  sanitizePath,
  secureJsonResponse
} from '@/lib/api-security';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

// Maximum file size: 5MB
const MAX_FILE_SIZE = 5 * 1024 * 1024;

// Allowed image types
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];

export async function POST(request: NextRequest) {
  try {
    // Rate limiting: 10 uploads per minute per IP
    const rateLimitResult = rateLimit(request, 10, 60000);
    if (!rateLimitResult.allowed) {
      return rateLimitResponse(rateLimitResult.resetTime);
    }

    const formData = await request.formData();
    const file = formData.get('file') as File;
    const productName = formData.get('productName') as string;

    // Validate file exists
    if (!file) {
      return secureJsonResponse({ error: 'No file provided' }, 400);
    }

    // Validate file with enhanced security
    const validation = validateFileUpload(file, {
      maxSize: MAX_FILE_SIZE,
      allowedTypes: ALLOWED_TYPES
    });

    if (!validation.valid) {
      return secureJsonResponse({ error: validation.error }, 400);
    }

    // Additional MIME type verification
    if (!ALLOWED_TYPES.includes(file.type)) {
      return secureJsonResponse({
        error: `Invalid file type. Allowed types: ${ALLOWED_TYPES.join(', ')}`
      }, 400);
    }

    // Sanitize and generate secure filename
    const timestamp = Date.now();
    const sanitizedProductName = sanitizePath(
      sanitizeInput(productName || 'product')
        .toLowerCase()
        .replace(/[^a-z0-9]/g, '-')
        .replace(/-+/g, '-')
        .substring(0, 50)
    );

    // Validate file extension
    const fileExt = file.name.split('.').pop()?.toLowerCase();
    const allowedExtensions = ['jpg', 'jpeg', 'png', 'webp'];

    if (!fileExt || !allowedExtensions.includes(fileExt)) {
      return secureJsonResponse({
        error: 'Invalid file extension. Allowed: jpg, jpeg, png, webp'
      }, 400);
    }

    const fileName = `${sanitizedProductName}-${timestamp}.${fileExt}`;
    const filePath = `product-images/${fileName}`;

    // Convert File to ArrayBuffer
    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    // Upload to Supabase Storage
    const { data, error } = await supabaseServer.storage
      .from('generated-videos')
      .upload(filePath, buffer, {
        contentType: file.type,
        cacheControl: '3600',
        upsert: false
      });

    if (error) {
      console.error('Supabase upload error:', error);
      return secureJsonResponse({ error: 'Failed to upload image' }, 500);
    }

    // Get public URL
    const { data: { publicUrl } } = supabaseServer.storage
      .from('generated-videos')
      .getPublicUrl(filePath);

    // Validate the generated URL
    if (!publicUrl || !isValidUrl(publicUrl)) {
      console.error('Invalid public URL generated:', publicUrl);
      return secureJsonResponse({ error: 'Failed to generate valid URL' }, 500);
    }

    return secureJsonResponse({
      success: true,
      url: publicUrl,
      path: filePath,
      fileName: fileName
    });

  } catch (error) {
    console.error('Upload error:', error);
    // Don't expose error details to client
    return secureJsonResponse(
      { error: 'An error occurred during upload' },
      500
    );
  }
}

// Helper function for URL validation
function isValidUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return ['http:', 'https:'].includes(parsed.protocol);
  } catch {
    return false;
  }
}
