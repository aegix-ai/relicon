/**
 * Analytics Context Helper
 *
 * Fetches user's analytics data to provide context for AI chat
 */

import { supabaseServer } from '@/lib/supabase-server';

export interface UserAnalytics {
  campaigns: {
    total: number;
    active: number;
    paused: number;
    completed: number;
  };
  performance: {
    totalSpend: number;
    totalRevenue: number;
    totalImpressions: number;
    totalReach: number;
    totalConversions: number;
    avgCTR: number;
    avgROAS: number;
    avgCPM: number;
    avgCPC: number;
  };
  topCampaigns: Array<{
    name: string;
    status: string;
    impressions: number;
    roas: number;
    spend: number;
    conversions: number;
  }>;
  recentPosts: Array<{
    caption: string;
    platform: string;
    impressions: number;
    engagement: number;
    ctr: number;
    publishedAt: string;
  }>;
  platforms: {
    instagram: boolean;
    facebook: boolean;
    tiktok: boolean;
  };
}

/**
 * Get comprehensive analytics context for AI chat
 */
export async function getUserAnalyticsContext(userId: string): Promise<UserAnalytics> {
  try {
    // Get campaign summary
    const { data: campaigns } = await supabaseServer
      .from('campaigns')
      .select('id, name, status, objective')
      .eq('user_id', userId);

    const campaignStats = {
      total: campaigns?.length || 0,
      active: campaigns?.filter(c => c.status === 'active').length || 0,
      paused: campaigns?.filter(c => c.status === 'paused').length || 0,
      completed: campaigns?.filter(c => c.status === 'completed').length || 0,
    };

    // Get performance metrics from campaign_performance view
    const { data: performanceData } = await supabaseServer
      .from('campaign_performance')
      .select('*')
      .eq('user_id', userId);

    // Calculate aggregate performance
    const performance = {
      totalSpend: performanceData?.reduce((sum, c) => sum + (c.spend_total || 0), 0) || 0,
      totalRevenue: performanceData?.reduce((sum, c) => sum + (c.total_conversions || 0) * 50, 0) || 0, // Assuming $50 per conversion
      totalImpressions: performanceData?.reduce((sum, c) => sum + (c.total_impressions || 0), 0) || 0,
      totalReach: performanceData?.reduce((sum, c) => sum + (c.total_reach || 0), 0) || 0,
      totalConversions: performanceData?.reduce((sum, c) => sum + (c.total_conversions || 0), 0) || 0,
      avgCTR: performanceData?.length ? performanceData.reduce((sum, c) => sum + (c.avg_ctr || 0), 0) / performanceData.length : 0,
      avgROAS: performanceData?.length ? performanceData.reduce((sum, c) => sum + (c.avg_roas || 0), 0) / performanceData.length : 0,
      avgCPM: performanceData?.length ? performanceData.reduce((sum, c) => sum + (c.avg_cpm || 0), 0) / performanceData.length : 0,
      avgCPC: performanceData?.length ? performanceData.reduce((sum, c) => sum + (c.avg_cpc || 0), 0) / performanceData.length : 0,
    };

    // Get top performing campaigns
    const topCampaigns = (performanceData || [])
      .sort((a, b) => (b.avg_roas || 0) - (a.avg_roas || 0))
      .slice(0, 5)
      .map(c => ({
        name: c.name,
        status: c.status,
        impressions: c.total_impressions || 0,
        roas: c.avg_roas || 0,
        spend: c.spend_total || 0,
        conversions: c.total_conversions || 0,
      }));

    // Get recent posts with analytics
    const { data: recentPosts } = await supabaseServer
      .from('post_performance')
      .select('*')
      .eq('user_id', userId)
      .order('published_at', { ascending: false })
      .limit(10);

    const posts = (recentPosts || []).map(p => ({
      caption: p.caption || 'Untitled post',
      platform: p.platform,
      impressions: p.impressions || 0,
      engagement: (p.likes || 0) + (p.comments || 0) + (p.shares || 0),
      ctr: p.ctr || 0,
      publishedAt: p.published_at || new Date().toISOString(),
    }));

    // Get connected platforms
    const { data: accounts } = await supabaseServer
      .from('social_accounts')
      .select('platform')
      .eq('user_id', userId)
      .eq('is_active', true);

    const platforms = {
      instagram: accounts?.some(a => a.platform === 'instagram') || false,
      facebook: accounts?.some(a => a.platform === 'facebook') || false,
      tiktok: accounts?.some(a => a.platform === 'tiktok') || false,
    };

    return {
      campaigns: campaignStats,
      performance,
      topCampaigns,
      recentPosts: posts,
      platforms,
    };
  } catch (error) {
    console.error('Error fetching analytics context:', error);

    // Return empty/default data on error
    return {
      campaigns: { total: 0, active: 0, paused: 0, completed: 0 },
      performance: {
        totalSpend: 0,
        totalRevenue: 0,
        totalImpressions: 0,
        totalReach: 0,
        totalConversions: 0,
        avgCTR: 0,
        avgROAS: 0,
        avgCPM: 0,
        avgCPC: 0,
      },
      topCampaigns: [],
      recentPosts: [],
      platforms: { instagram: false, facebook: false, tiktok: false },
    };
  }
}

/**
 * Format analytics context as a prompt for the AI
 */
export function formatAnalyticsForPrompt(analytics: UserAnalytics): string {
  const { campaigns, performance, topCampaigns, recentPosts, platforms } = analytics;

  const connectedPlatforms = Object.entries(platforms)
    .filter(([_, connected]) => connected)
    .map(([platform]) => platform)
    .join(', ') || 'none';

  let prompt = `
# User's Current Analytics Data

## Campaign Overview
- Total Campaigns: ${campaigns.total}
- Active: ${campaigns.active}
- Paused: ${campaigns.paused}
- Completed: ${campaigns.completed}

## Overall Performance Metrics
- Total Spend: $${performance.totalSpend.toFixed(2)}
- Total Revenue: $${performance.totalRevenue.toFixed(2)}
- Total Impressions: ${performance.totalImpressions.toLocaleString()}
- Total Reach: ${performance.totalReach.toLocaleString()}
- Total Conversions: ${performance.totalConversions}
- Average CTR: ${performance.avgCTR.toFixed(2)}%
- Average ROAS: ${performance.avgROAS.toFixed(0)}%
- Average CPM: $${performance.avgCPM.toFixed(2)}
- Average CPC: $${performance.avgCPC.toFixed(2)}

## Connected Platforms
${connectedPlatforms}
`;

  // Add top campaigns if available
  if (topCampaigns.length > 0) {
    prompt += `\n## Top Performing Campaigns\n`;
    topCampaigns.forEach((campaign, i) => {
      prompt += `
${i + 1}. ${campaign.name} (${campaign.status})
   - Impressions: ${campaign.impressions.toLocaleString()}
   - ROAS: ${campaign.roas.toFixed(0)}%
   - Spend: $${campaign.spend.toFixed(2)}
   - Conversions: ${campaign.conversions}
`;
    });
  }

  // Add recent posts if available
  if (recentPosts.length > 0) {
    prompt += `\n## Recent Posts (Last ${recentPosts.length})\n`;
    recentPosts.slice(0, 5).forEach((post, i) => {
      prompt += `
${i + 1}. ${post.platform} - "${post.caption.substring(0, 50)}${post.caption.length > 50 ? '...' : ''}"
   - Impressions: ${post.impressions.toLocaleString()}
   - Engagement: ${post.engagement}
   - CTR: ${post.ctr.toFixed(2)}%
`;
    });
  }

  return prompt;
}
