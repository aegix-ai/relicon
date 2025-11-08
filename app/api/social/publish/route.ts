import { NextRequest, NextResponse } from 'next/server';
import { supabaseServer } from '@/lib/supabase-server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * POST /api/social/publish
 * Publish a generated video to social media platforms
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const {
      videoId,
      socialAccountId,
      caption,
      hashtags = [],
      scheduledFor,
      campaignId
    } = body;

    // Validate required fields
    if (!videoId || !socialAccountId) {
      return NextResponse.json(
        { error: 'Video ID and social account ID are required' },
        { status: 400 }
      );
    }

    // Get video details
    const { data: video, error: videoError } = await supabaseServer
      .from('generated_videos')
      .select('*')
      .eq('id', videoId)
      .single();

    if (videoError || !video) {
      return NextResponse.json(
        { error: 'Video not found' },
        { status: 404 }
      );
    }

    // Get social account details
    const { data: account, error: accountError } = await supabaseServer
      .from('social_accounts')
      .select('*')
      .eq('id', socialAccountId)
      .single();

    if (accountError || !account) {
      return NextResponse.json(
        { error: 'Social account not found' },
        { status: 404 }
      );
    }

    // Check if video URL is accessible
    if (!video.video_url) {
      return NextResponse.json(
        { error: 'Video URL not available' },
        { status: 400 }
      );
    }

    // If scheduled, create draft post
    if (scheduledFor) {
      const { data: post, error: postError } = await supabaseServer
        .from('social_posts')
        .insert({
          user_id: account.user_id,
          campaign_id: campaignId,
          video_id: videoId,
          social_account_id: socialAccountId,
          platform: account.platform,
          caption: caption,
          hashtags: hashtags,
          status: 'scheduled',
          scheduled_for: scheduledFor
        })
        .select()
        .single();

      if (postError) {
        console.error('Error creating scheduled post:', postError);
        return NextResponse.json(
          { error: 'Failed to schedule post' },
          { status: 500 }
        );
      }

      return NextResponse.json({
        success: true,
        message: 'Post scheduled successfully',
        post: post
      });
    }

    // Publish immediately based on platform
    let platformPostId;
    let permalink;

    try {
      switch (account.platform) {
        case 'instagram':
          const igResult = await publishToInstagram(
            account.platform_user_id,
            account.access_token,
            video.video_url,
            caption,
            hashtags
          );
          platformPostId = igResult.id;
          permalink = igResult.permalink;
          break;

        case 'facebook':
          const fbResult = await publishToFacebook(
            account.platform_user_id,
            account.access_token,
            video.video_url,
            caption + (hashtags.length ? '\n\n' + hashtags.map(t => `#${t}`).join(' ') : '')
          );
          platformPostId = fbResult.id;
          permalink = fbResult.permalink;
          break;

        case 'tiktok':
          const ttResult = await publishToTikTok(
            account.access_token,
            video.video_url,
            caption,
            hashtags
          );
          platformPostId = ttResult.publish_id;
          permalink = ttResult.share_url;
          break;

        default:
          throw new Error(`Unsupported platform: ${account.platform}`);
      }

      // Store the published post
      const { data: post, error: postError } = await supabaseServer
        .from('social_posts')
        .insert({
          user_id: account.user_id,
          campaign_id: campaignId,
          video_id: videoId,
          social_account_id: socialAccountId,
          platform: account.platform,
          platform_post_id: platformPostId,
          caption: caption,
          hashtags: hashtags,
          status: 'published',
          published_at: new Date().toISOString(),
          permalink: permalink
        })
        .select()
        .single();

      if (postError) {
        console.error('Error storing published post:', postError);
        // Don't fail the request since post was published
      }

      return NextResponse.json({
        success: true,
        message: 'Video published successfully',
        post: post,
        platform_post_id: platformPostId,
        permalink: permalink
      });

    } catch (publishError: any) {
      console.error('Publishing error:', publishError);

      // Store failed post
      await supabaseServer
        .from('social_posts')
        .insert({
          user_id: account.user_id,
          campaign_id: campaignId,
          video_id: videoId,
          social_account_id: socialAccountId,
          platform: account.platform,
          caption: caption,
          hashtags: hashtags,
          status: 'failed',
          error_message: publishError.message || 'Unknown error'
        });

      return NextResponse.json(
        { error: publishError.message || 'Failed to publish video' },
        { status: 500 }
      );
    }

  } catch (error: any) {
    console.error('Publish API error:', error);
    return NextResponse.json(
      { error: 'Failed to publish video' },
      { status: 500 }
    );
  }
}

// ============================================================================
// Platform Publishing Functions
// ============================================================================

async function publishToInstagram(
  instagramAccountId: string,
  accessToken: string,
  videoUrl: string,
  caption: string,
  hashtags: string[]
) {
  const fullCaption = caption + (hashtags.length ? '\n\n' + hashtags.map(t => `#${t}`).join(' ') : '');

  // Step 1: Create media container
  const containerResponse = await fetch(
    `https://graph.facebook.com/v18.0/${instagramAccountId}/media`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        media_type: 'REELS',
        video_url: videoUrl,
        caption: fullCaption,
        share_to_feed: true,
        access_token: accessToken
      })
    }
  );

  const containerData = await containerResponse.json();

  if (!containerResponse.ok || containerData.error) {
    throw new Error(containerData.error?.message || 'Failed to create Instagram media container');
  }

  const containerId = containerData.id;

  // Step 2: Wait for container to be ready (poll status)
  let isReady = false;
  let attempts = 0;
  const maxAttempts = 30; // 30 attempts x 10 seconds = 5 minutes max

  while (!isReady && attempts < maxAttempts) {
    await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10 seconds

    const statusResponse = await fetch(
      `https://graph.facebook.com/v18.0/${containerId}?fields=status_code&access_token=${accessToken}`
    );
    const statusData = await statusResponse.json();

    if (statusData.status_code === 'FINISHED') {
      isReady = true;
    } else if (statusData.status_code === 'ERROR') {
      throw new Error('Instagram media processing failed');
    }

    attempts++;
  }

  if (!isReady) {
    throw new Error('Instagram media processing timed out');
  }

  // Step 3: Publish the container
  const publishResponse = await fetch(
    `https://graph.facebook.com/v18.0/${instagramAccountId}/media_publish`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        creation_id: containerId,
        access_token: accessToken
      })
    }
  );

  const publishData = await publishResponse.json();

  if (!publishResponse.ok || publishData.error) {
    throw new Error(publishData.error?.message || 'Failed to publish Instagram media');
  }

  // Get permalink
  const mediaResponse = await fetch(
    `https://graph.facebook.com/v18.0/${publishData.id}?fields=permalink&access_token=${accessToken}`
  );
  const mediaData = await mediaResponse.json();

  return {
    id: publishData.id,
    permalink: mediaData.permalink
  };
}

async function publishToFacebook(
  pageId: string,
  accessToken: string,
  videoUrl: string,
  description: string
) {
  const response = await fetch(
    `https://graph.facebook.com/v18.0/${pageId}/videos`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        file_url: videoUrl,
        description: description,
        published: true,
        access_token: accessToken
      })
    }
  );

  const data = await response.json();

  if (!response.ok || data.error) {
    throw new Error(data.error?.message || 'Failed to publish to Facebook');
  }

  // Get video permalink
  const videoResponse = await fetch(
    `https://graph.facebook.com/v18.0/${data.id}?fields=permalink_url&access_token=${accessToken}`
  );
  const videoData = await videoResponse.json();

  return {
    id: data.id,
    permalink: videoData.permalink_url
  };
}

async function publishToTikTok(
  accessToken: string,
  videoUrl: string,
  title: string,
  hashtags: string[]
) {
  const fullTitle = title + (hashtags.length ? ' ' + hashtags.map(t => `#${t}`).join(' ') : '');

  // Note: TikTok API requires uploading the video file directly
  // For now, we'll return an error message explaining this
  throw new Error(
    'TikTok requires direct file upload. Please download the video and upload manually, or implement direct file upload.'
  );

  // TODO: Implement TikTok video upload flow
  // This requires:
  // 1. Downloading the video from videoUrl
  // 2. Uploading to TikTok's upload endpoint
  // 3. Publishing the video

  /* Example implementation:
  // Step 1: Download video
  const videoResponse = await fetch(videoUrl);
  const videoBlob = await videoResponse.blob();

  // Step 2: Initialize upload
  const initResponse = await fetch(
    'https://open.tiktokapis.com/v2/post/publish/video/init/',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        post_info: {
          title: fullTitle,
          privacy_level: 'PUBLIC_TO_EVERYONE',
          disable_duet: false,
          disable_comment: false,
          disable_stitch: false
        },
        source_info: {
          source: 'FILE_UPLOAD',
          video_size: videoBlob.size,
          chunk_size: videoBlob.size,
          total_chunk_count: 1
        }
      })
    }
  );

  const initData = await initResponse.json();
  const { publish_id, upload_url } = initData.data;

  // Step 3: Upload video
  await fetch(upload_url, {
    method: 'PUT',
    headers: { 'Content-Type': 'video/mp4' },
    body: videoBlob
  });

  return {
    publish_id: publish_id,
    share_url: `https://www.tiktok.com/@username/video/${publish_id}`
  };
  */
}
