import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * GET /api/social/connect/meta
 * Initiates OAuth flow for Meta (Facebook/Instagram)
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId'); // In production, get from session

    if (!userId) {
      return NextResponse.json(
        { error: 'User ID is required' },
        { status: 400 }
      );
    }

    const appId = process.env.NEXT_PUBLIC_META_APP_ID;
    const redirectUri = process.env.META_REDIRECT_URI || 'http://localhost:5000/api/social/callback/meta';

    if (!appId) {
      return NextResponse.json(
        { error: 'Meta App ID not configured' },
        { status: 500 }
      );
    }

    // Scopes needed for Instagram and Facebook posting + analytics
    const scopes = [
      'pages_show_list',
      'pages_read_engagement',
      'pages_manage_posts',
      'pages_read_user_content',
      'instagram_basic',
      'instagram_content_publish',
      'instagram_manage_comments',
      'instagram_manage_insights',
      'business_management'
    ].join(',');

    // Build Meta OAuth URL
    const authUrl = new URL('https://www.facebook.com/v18.0/dialog/oauth');
    authUrl.searchParams.set('client_id', appId);
    authUrl.searchParams.set('redirect_uri', redirectUri);
    authUrl.searchParams.set('scope', scopes);
    authUrl.searchParams.set('response_type', 'code');
    authUrl.searchParams.set('state', userId); // Pass user ID in state

    return NextResponse.redirect(authUrl.toString());
  } catch (error) {
    console.error('Meta OAuth initiation error:', error);
    return NextResponse.json(
      { error: 'Failed to initiate Meta OAuth' },
      { status: 500 }
    );
  }
}
