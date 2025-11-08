import { NextRequest, NextResponse } from 'next/server';
import { supabaseServer } from '@/lib/supabase-server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * POST /api/social/analytics/sync
 * Sync analytics data from social media platforms
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { userId, platform, postIds } = body;

    if (!userId) {
      return NextResponse.json(
        { error: 'User ID is required' },
        { status: 400 }
      );
    }

    // Start sync log
    const { data: syncLog, error: logError } = await supabaseServer
      .from('analytics_sync_log')
      .insert({
        user_id: userId,
        platform: platform || 'all',
        sync_type: 'analytics',
        status: 'running',
        started_at: new Date().toISOString()
      })
      .select()
      .single();

    if (logError) {
      console.error('Error creating sync log:', logError);
    }

    let totalSynced = 0;
    const errors = [];

    try {
      // Get posts to sync
      let query = supabaseServer
        .from('social_posts')
        .select('*, social_accounts(*)')
        .eq('user_id', userId)
        .eq('status', 'published')
        .not('platform_post_id', 'is', null);

      if (platform) {
        query = query.eq('platform', platform);
      }

      if (postIds && postIds.length > 0) {
        query = query.in('id', postIds);
      }

      const { data: posts, error: postsError } = await query;

      if (postsError) {
        throw postsError;
      }

      // Sync analytics for each post
      for (const post of posts || []) {
        try {
          let analytics;

          switch (post.platform) {
            case 'instagram':
              analytics = await getInstagramInsights(
                post.platform_post_id!,
                post.social_accounts.access_token
              );
              break;

            case 'facebook':
              analytics = await getFacebookVideoInsights(
                post.platform_post_id!,
                post.social_accounts.access_token
              );
              break;

            case 'tiktok':
              analytics = await getTikTokAnalytics(
                post.platform_post_id!,
                post.social_accounts.access_token
              );
              break;

            default:
              continue;
          }

          // Store analytics
          await supabaseServer
            .from('post_analytics')
            .upsert({
              post_id: post.id,
              ...analytics,
              metrics_date: new Date().toISOString().split('T')[0],
              synced_at: new Date().toISOString()
            }, {
              onConflict: 'post_id,metrics_date'
            });

          totalSynced++;
        } catch (postError: any) {
          console.error(`Error syncing post ${post.id}:`, postError);
          errors.push({
            postId: post.id,
            error: postError.message
          });
        }
      }

      // Update sync log
      if (syncLog) {
        await supabaseServer
          .from('analytics_sync_log')
          .update({
            status: errors.length > 0 ? 'partial' : 'success',
            records_synced: totalSynced,
            error_message: errors.length > 0 ? JSON.stringify(errors) : null,
            completed_at: new Date().toISOString()
          })
          .eq('id', syncLog.id);
      }

      // Update campaign analytics
      await updateCampaignAnalytics(userId);

      return NextResponse.json({
        success: true,
        synced: totalSynced,
        errors: errors.length,
        message: `Synced ${totalSynced} posts${errors.length > 0 ? ` with ${errors.length} errors` : ''}`
      });

    } catch (syncError: any) {
      // Update sync log with error
      if (syncLog) {
        await supabaseServer
          .from('analytics_sync_log')
          .update({
            status: 'failed',
            error_message: syncError.message,
            completed_at: new Date().toISOString()
          })
          .eq('id', syncLog.id);
      }

      throw syncError;
    }

  } catch (error: any) {
    console.error('Analytics sync error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to sync analytics' },
      { status: 500 }
    );
  }
}

// ============================================================================
// Platform Analytics Functions
// ============================================================================

async function getInstagramInsights(
  mediaId: string,
  accessToken: string
) {
  const metrics = [
    'impressions',
    'reach',
    'likes',
    'comments',
    'shares',
    'saves',
    'plays',
    'total_interactions'
  ];

  const response = await fetch(
    `https://graph.facebook.com/v18.0/${mediaId}/insights?` +
    `metric=${metrics.join(',')}&access_token=${accessToken}`
  );

  if (!response.ok) {
    throw new Error('Failed to fetch Instagram insights');
  }

  const { data } = await response.json();

  // Transform to our schema
  return {
    impressions: data.find((m: any) => m.name === 'impressions')?.values[0]?.value || 0,
    reach: data.find((m: any) => m.name === 'reach')?.values[0]?.value || 0,
    likes: data.find((m: any) => m.name === 'likes')?.values[0]?.value || 0,
    comments: data.find((m: any) => m.name === 'comments')?.values[0]?.value || 0,
    shares: data.find((m: any) => m.name === 'shares')?.values[0]?.value || 0,
    saves: data.find((m: any) => m.name === 'saves')?.values[0]?.value || 0,
    views: data.find((m: any) => m.name === 'plays')?.values[0]?.value || 0,
    clicks: data.find((m: any) => m.name === 'total_interactions')?.values[0]?.value || 0
  };
}

async function getFacebookVideoInsights(
  videoId: string,
  accessToken: string
) {
  const response = await fetch(
    `https://graph.facebook.com/v18.0/${videoId}?` +
    `fields=views,likes.summary(true),comments.summary(true),shares,reactions.summary(true)` +
    `&access_token=${accessToken}`
  );

  if (!response.ok) {
    throw new Error('Failed to fetch Facebook video insights');
  }

  const data = await response.json();

  return {
    views: data.views || 0,
    likes: data.likes?.summary?.total_count || 0,
    comments: data.comments?.summary?.total_count || 0,
    shares: data.shares?.count || 0,
    reach: data.views || 0, // Approximation
    impressions: Math.round((data.views || 0) * 1.5) // Approximation
  };
}

async function getTikTokAnalytics(
  videoId: string,
  accessToken: string
) {
  const response = await fetch(
    'https://open.tiktokapis.com/v2/video/query/',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        filters: {
          video_ids: [videoId]
        },
        fields: ['id', 'view_count', 'like_count', 'comment_count', 'share_count']
      })
    }
  );

  if (!response.ok) {
    throw new Error('Failed to fetch TikTok analytics');
  }

  const { data } = await response.json();
  const video = data?.videos?.[0];

  if (!video) {
    throw new Error('TikTok video not found');
  }

  return {
    views: video.view_count || 0,
    likes: video.like_count || 0,
    comments: video.comment_count || 0,
    shares: video.share_count || 0,
    reach: video.view_count || 0, // TikTok doesn't provide separate reach
    impressions: Math.round((video.view_count || 0) * 1.2) // Approximation
  };
}

// ============================================================================
// Campaign Analytics Aggregation
// ============================================================================

async function updateCampaignAnalytics(userId: string) {
  // Get all campaigns
  const { data: campaigns } = await supabaseServer
    .from('campaigns')
    .select('id')
    .eq('user_id', userId);

  if (!campaigns) return;

  for (const campaign of campaigns) {
    // Aggregate analytics from all posts in campaign
    const { data: posts } = await supabaseServer
      .from('social_posts')
      .select('id, post_analytics(*)')
      .eq('campaign_id', campaign.id)
      .eq('status', 'published');

    if (!posts || posts.length === 0) continue;

    // Sum up all metrics
    let totalImpressions = 0;
    let totalReach = 0;
    let totalLikes = 0;
    let totalComments = 0;
    let totalShares = 0;
    let totalSaves = 0;
    let totalViews = 0;
    let totalClicks = 0;
    let totalConversions = 0;
    let totalConversionValue = 0;
    let totalSpend = 0;

    for (const post of posts) {
      const analytics = post.post_analytics?.[0];
      if (analytics) {
        totalImpressions += analytics.impressions || 0;
        totalReach += analytics.reach || 0;
        totalLikes += analytics.likes || 0;
        totalComments += analytics.comments || 0;
        totalShares += analytics.shares || 0;
        totalSaves += analytics.saves || 0;
        totalViews += analytics.views || 0;
        totalClicks += analytics.clicks || 0;
        totalConversions += analytics.conversions || 0;
        totalConversionValue += analytics.conversion_value || 0;
        totalSpend += analytics.spend || 0;
      }
    }

    // Calculate averages
    const avgCTR = totalImpressions > 0 ? (totalClicks / totalImpressions) * 100 : 0;
    const avgCPM = totalImpressions > 0 ? (totalSpend / totalImpressions) * 1000 : 0;
    const avgCPC = totalClicks > 0 ? totalSpend / totalClicks : 0;
    const avgCPA = totalConversions > 0 ? totalSpend / totalConversions : 0;
    const totalROAS = totalSpend > 0 ? (totalConversionValue / totalSpend) * 100 : 0;

    // Update campaign analytics
    await supabaseServer
      .from('campaign_analytics')
      .upsert({
        campaign_id: campaign.id,
        total_impressions: totalImpressions,
        total_reach: totalReach,
        total_likes: totalLikes,
        total_comments: totalComments,
        total_shares: totalShares,
        total_saves: totalSaves,
        total_views: totalViews,
        total_clicks: totalClicks,
        avg_ctr: Number(avgCTR.toFixed(2)),
        total_conversions: totalConversions,
        total_conversion_value: totalConversionValue,
        total_spend: totalSpend,
        avg_cpm: Number(avgCPM.toFixed(2)),
        avg_cpc: Number(avgCPC.toFixed(2)),
        avg_cpa: Number(avgCPA.toFixed(2)),
        total_roas: Number(totalROAS.toFixed(2)),
        metrics_date: new Date().toISOString().split('T')[0],
        synced_at: new Date().toISOString()
      }, {
        onConflict: 'campaign_id,metrics_date'
      });

    // Update campaign spend
    await supabaseServer
      .from('campaigns')
      .update({ spend_total: totalSpend })
      .eq('id', campaign.id);
  }
}
