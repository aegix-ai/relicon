import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

// Rate limiting store (in-memory, use Redis in production)
const rateLimitStore = new Map<string, { count: number; resetTime: number }>();

/**
 * Rate limiting middleware
 * Limits requests per IP address
 */
export function rateLimit(
  request: NextRequest,
  limit: number = 10,
  windowMs: number = 60000 // 1 minute
): { allowed: boolean; remaining: number; resetTime: number } {
  const ip = request.ip || request.headers.get('x-forwarded-for') || 'unknown';
  const key = `rate_limit:${ip}`;
  const now = Date.now();

  const record = rateLimitStore.get(key);

  if (!record || now > record.resetTime) {
    // Create new record
    rateLimitStore.set(key, {
      count: 1,
      resetTime: now + windowMs
    });

    return {
      allowed: true,
      remaining: limit - 1,
      resetTime: now + windowMs
    };
  }

  if (record.count >= limit) {
    return {
      allowed: false,
      remaining: 0,
      resetTime: record.resetTime
    };
  }

  // Increment count
  record.count++;

  return {
    allowed: true,
    remaining: limit - record.count,
    resetTime: record.resetTime
  };
}

/**
 * Create rate limit response
 */
export function rateLimitResponse(resetTime: number): NextResponse {
  const retryAfter = Math.ceil((resetTime - Date.now()) / 1000);

  return NextResponse.json(
    {
      error: 'Too many requests',
      message: 'Rate limit exceeded. Please try again later.',
      retryAfter
    },
    {
      status: 429,
      headers: {
        'Retry-After': retryAfter.toString(),
        'X-RateLimit-Remaining': '0'
      }
    }
  );
}

/**
 * Validate API key from request headers
 */
export function validateApiKey(request: NextRequest): boolean {
  const apiKey = request.headers.get('x-api-key');
  const validApiKey = process.env.ADMIN_API_KEY;

  if (!validApiKey) {
    console.warn('ADMIN_API_KEY not configured');
    return false;
  }

  return apiKey === validApiKey;
}

/**
 * Input sanitization - prevent XSS
 */
export function sanitizeInput(input: string): string {
  if (typeof input !== 'string') return '';

  return input
    .replace(/[<>]/g, '') // Remove < and >
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+\s*=/gi, '') // Remove event handlers
    .trim();
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate URL format
 */
export function isValidUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return ['http:', 'https:'].includes(parsed.protocol);
  } catch {
    return false;
  }
}

/**
 * Validate file upload
 */
export function validateFileUpload(
  file: File,
  options: {
    maxSize?: number; // in bytes
    allowedTypes?: string[];
  } = {}
): { valid: boolean; error?: string } {
  const { maxSize = 5 * 1024 * 1024, allowedTypes = ['image/jpeg', 'image/png', 'image/webp'] } = options;

  // Check file size
  if (file.size > maxSize) {
    return {
      valid: false,
      error: `File size exceeds maximum allowed size of ${maxSize / 1024 / 1024}MB`
    };
  }

  // Check file type
  if (!allowedTypes.includes(file.type)) {
    return {
      valid: false,
      error: `File type ${file.type} is not allowed. Allowed types: ${allowedTypes.join(', ')}`
    };
  }

  return { valid: true };
}

/**
 * Generate secure random token
 */
export function generateSecureToken(length: number = 32): string {
  return crypto.randomBytes(length).toString('hex');
}

/**
 * Hash sensitive data
 */
export function hashData(data: string): string {
  return crypto.createHash('sha256').update(data).digest('hex');
}

/**
 * Verify CSRF token
 */
export function verifyCsrfToken(request: NextRequest, token: string): boolean {
  const headerToken = request.headers.get('x-csrf-token');
  return headerToken === token;
}

/**
 * Validate JSON request body
 */
export function validateJsonBody(body: any, requiredFields: string[]): { valid: boolean; error?: string } {
  if (!body || typeof body !== 'object') {
    return { valid: false, error: 'Invalid request body' };
  }

  for (const field of requiredFields) {
    if (!(field in body)) {
      return { valid: false, error: `Missing required field: ${field}` };
    }
  }

  return { valid: true };
}

/**
 * SQL Injection prevention (for raw queries, not needed with Supabase)
 */
export function sanitizeSqlInput(input: string): string {
  return input
    .replace(/'/g, "''") // Escape single quotes
    .replace(/;/g, '') // Remove semicolons
    .replace(/--/g, '') // Remove SQL comments
    .replace(/\/\*/g, '') // Remove multi-line comments
    .replace(/\*\//g, '');
}

/**
 * Path traversal prevention
 */
export function sanitizePath(path: string): string {
  return path.replace(/\.\./g, '').replace(/\//g, '_');
}

/**
 * Command injection prevention
 */
export function sanitizeCommand(input: string): string {
  return input
    .replace(/[;&|`$()]/g, '') // Remove shell metacharacters
    .replace(/\n/g, '');
}

/**
 * Create secure response with headers
 */
export function secureJsonResponse(data: any, status: number = 200): NextResponse {
  return NextResponse.json(data, {
    status,
    headers: {
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'X-XSS-Protection': '1; mode=block',
      'Cache-Control': 'no-store, no-cache, must-revalidate, private'
    }
  });
}

/**
 * Validate environment in production
 */
export function validateProductionEnv(): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (process.env.NODE_ENV === 'production') {
    // Check required environment variables
    const required = [
      'NEXT_PUBLIC_SUPABASE_URL',
      'SUPABASE_SERVICE_ROLE_KEY',
      'ADMIN_API_KEY',
      'CRON_SECRET'
    ];

    for (const key of required) {
      if (!process.env[key]) {
        errors.push(`Missing required environment variable: ${key}`);
      }
    }

    // Check API keys are not default/example values
    if (process.env.ADMIN_API_KEY === 'your-admin-api-key-here') {
      errors.push('ADMIN_API_KEY is still set to default value');
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
}
