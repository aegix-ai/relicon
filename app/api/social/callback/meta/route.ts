import { NextRequest, NextResponse } from 'next/server';
import { supabaseServer } from '@/lib/supabase-server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * GET /api/social/callback/meta
 * OAuth callback from Meta (Facebook/Instagram)
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const code = searchParams.get('code');
    const state = searchParams.get('state'); // userId
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

    const userId = state;

    // Exchange code for access token
    const tokenResponse = await fetch(
      `https://graph.facebook.com/v18.0/oauth/access_token?` +
      `client_id=${process.env.NEXT_PUBLIC_META_APP_ID}` +
      `&client_secret=${process.env.META_APP_SECRET}` +
      `&redirect_uri=${process.env.META_REDIRECT_URI}` +
      `&code=${code}`
    );

    if (!tokenResponse.ok) {
      throw new Error('Failed to exchange code for token');
    }

    const tokenData = await tokenResponse.json();
    const accessToken = tokenData.access_token;

    // Get user's Facebook pages
    const pagesResponse = await fetch(
      `https://graph.facebook.com/v18.0/me/accounts?` +
      `fields=id,name,access_token,instagram_business_account{id,username,name,profile_picture_url}` +
      `&access_token=${accessToken}`
    );

    const pagesData = await pagesResponse.json();

    // Store each connected account
    const accounts = [];

    for (const page of pagesData.data || []) {
      // Store Facebook page
      const { error: fbError } = await supabaseServer
        .from('social_accounts')
        .upsert({
          user_id: userId,
          platform: 'facebook',
          platform_user_id: page.id,
          username: page.name,
          display_name: page.name,
          access_token: page.access_token,
          account_type: 'business',
          is_active: true,
          connected_at: new Date().toISOString()
        }, {
          onConflict: 'platform,platform_user_id'
        });

      if (fbError) {
        console.error('Error saving Facebook account:', fbError);
      } else {
        accounts.push({ platform: 'facebook', name: page.name });
      }

      // Store Instagram account if linked
      if (page.instagram_business_account) {
        const ig = page.instagram_business_account;
        const { error: igError } = await supabaseServer
          .from('social_accounts')
          .upsert({
            user_id: userId,
            platform: 'instagram',
            platform_user_id: ig.id,
            username: ig.username,
            display_name: ig.name,
            profile_image_url: ig.profile_picture_url,
            access_token: page.access_token, // Use page token for Instagram
            account_type: 'business',
            is_active: true,
            connected_at: new Date().toISOString()
          }, {
            onConflict: 'platform,platform_user_id'
          });

        if (igError) {
          console.error('Error saving Instagram account:', igError);
        } else {
          accounts.push({ platform: 'instagram', name: ig.username });
        }
      }
    }

    // Redirect back to settings with success message
    const appUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:5000';
    return NextResponse.redirect(
      `${appUrl}/dashboard/settings?connected=${accounts.length}&accounts=${encodeURIComponent(JSON.stringify(accounts))}`
    );
  } catch (error) {
    console.error('Meta OAuth callback error:', error);
    const appUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:5000';
    return NextResponse.redirect(
      `${appUrl}/dashboard/settings?error=connection_failed`
    );
  }
}
