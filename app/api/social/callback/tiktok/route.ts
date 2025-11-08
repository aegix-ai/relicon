import { NextRequest, NextResponse } from 'next/server';
import { supabaseServer } from '@/lib/supabase-server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * GET /api/social/callback/tiktok
 * OAuth callback from TikTok
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const error = searchParams.get('error');

    if (error) {
      return NextResponse.redirect(
        `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:5000'}/dashboard/settings?error=${error}`
      );
    }

    if (!code || !state) {
      return NextResponse.json(
        { error: 'Missing code or state parameter' },
        { status: 400 }
      );
    }

    // Decode state to get user ID
    const decoded = Buffer.from(state, 'base64').toString('utf-8');
    const [userId] = decoded.split(':');

    // Exchange code for access token
    const tokenResponse = await fetch('https://open.tiktokapis.com/v2/oauth/token/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
      },
      body: new URLSearchParams({
        client_key: process.env.NEXT_PUBLIC_TIKTOK_CLIENT_KEY!,
        client_secret: process.env.TIKTOK_CLIENT_SECRET!,
        code: code,
        grant_type: 'authorization_code',
        redirect_uri: process.env.TIKTOK_REDIRECT_URI!
      })
    });

    if (!tokenResponse.ok) {
      throw new Error('Failed to exchange code for token');
    }

    const tokenData = await tokenResponse.json();
    const { access_token, refresh_token, expires_in, open_id } = tokenData;

    // Get user info
    const userResponse = await fetch('https://open.tiktokapis.com/v2/user/info/?fields=open_id,union_id,avatar_url,display_name,username', {
      headers: {
        'Authorization': `Bearer ${access_token}`
      }
    });

    const userData = await userResponse.json();
    const user = userData.data?.user;

    if (!user) {
      throw new Error('Failed to get user info');
    }

    // Calculate token expiry
    const expiresAt = new Date(Date.now() + expires_in * 1000);

    // Store TikTok account
    const { error: dbError } = await supabaseServer
      .from('social_accounts')
      .upsert({
        user_id: userId,
        platform: 'tiktok',
        platform_user_id: open_id,
        username: user.username || user.display_name,
        display_name: user.display_name,
        profile_image_url: user.avatar_url,
        access_token: access_token,
        refresh_token: refresh_token,
        token_expires_at: expiresAt.toISOString(),
        account_type: 'personal',
        is_active: true,
        connected_at: new Date().toISOString()
      }, {
        onConflict: 'platform,platform_user_id'
      });

    if (dbError) {
      console.error('Error saving TikTok account:', dbError);
      throw dbError;
    }

    // Redirect back to settings with success message
    const appUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:5000';
    return NextResponse.redirect(
      `${appUrl}/dashboard/settings?connected=1&platform=tiktok&username=${user.username || user.display_name}`
    );
  } catch (error) {
    console.error('TikTok OAuth callback error:', error);
    const appUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:5000';
    return NextResponse.redirect(
      `${appUrl}/dashboard/settings?error=connection_failed`
    );
  }
}
