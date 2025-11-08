import { NextRequest, NextResponse } from 'next/server';
import { supabaseServer } from '@/lib/supabase-server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * GET /api/cron/sync-analytics
 * Automated analytics sync - run hourly via cron
 *
 * Vercel Cron: Add to vercel.json:
 * {
 *   "crons": [{
 *     "path": "/api/cron/sync-analytics",
 *     "schedule": "0 * * * *"
 *   }]
 * }
 */
export async function GET(request: NextRequest) {
  try {
    // Verify cron secret (for security)
    const authHeader = request.headers.get('authorization');
    const cronSecret = process.env.CRON_SECRET || 'dev-secret';

    if (authHeader !== `Bearer ${cronSecret}`) {
      return new Response('Unauthorized', { status: 401 });
    }

    console.log('[CRON] Starting analytics sync...');

    // Get all active users with social accounts
    const { data: accounts, error: accountsError } = await supabaseServer
      .from('social_accounts')
      .select('user_id')
      .eq('is_active', true);

    if (accountsError) {
      throw accountsError;
    }

    // Get unique user IDs
    const userIds = [...new Set(accounts?.map(acc => acc.user_id) || [])];

    console.log(`[CRON] Found ${userIds.length} users with active social accounts`);

    const results = {
      total_users: userIds.length,
      successful: 0,
      failed: 0,
      total_posts_synced: 0
    };

    // Sync analytics for each user
    for (const userId of userIds) {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:5000'}/api/social/analytics/sync`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ userId })
          }
        );

        const data = await response.json();

        if (data.success) {
          results.successful++;
          results.total_posts_synced += data.synced || 0;
          console.log(`[CRON] ✓ User ${userId}: Synced ${data.synced} posts`);
        } else {
          results.failed++;
          console.error(`[CRON] ✗ User ${userId}: ${data.error}`);
        }
      } catch (userError) {
        results.failed++;
        console.error(`[CRON] ✗ User ${userId}:`, userError);
      }
    }

    console.log('[CRON] Analytics sync complete:', results);

    return NextResponse.json({
      success: true,
      message: 'Analytics sync completed',
      ...results,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('[CRON] Analytics sync failed:', error);

    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Analytics sync failed',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}
