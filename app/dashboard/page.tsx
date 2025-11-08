import { MetricCard } from "@/components/dashboard/MetricCard"
import { PerformanceChart } from "@/components/dashboard/PerformanceChart"
import { CampaignTable } from "@/components/dashboard/CampaignTable"
import { supabaseServer } from "@/lib/supabase-server"

async function getDashboardData() {
  try {
    // Get user analytics summary
    const { data: analytics } = await supabaseServer
      .from('user_analytics_summary')
      .select('*')
      .single()

    // Get recent campaigns
    const { data: campaigns } = await supabaseServer
      .from('campaigns')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(5)

    // Get video generation count
    const { count: videoCount } = await supabaseServer
      .from('generated_videos')
      .select('*', { count: 'exact', head: true })

    return {
      analytics: analytics || {
        total_spend: 0,
        total_conversions: 0,
        total_clicks: 0,
        total_impressions: 0,
        avg_ctr: 0,
        avg_roas: 0
      },
      campaigns: campaigns || [],
      videoCount: videoCount || 0
    }
  } catch (error) {
    console.error('Error fetching dashboard data:', error)
    return {
      analytics: {
        total_spend: 0,
        total_conversions: 0,
        total_clicks: 0,
        total_impressions: 0,
        avg_ctr: 0,
        avg_roas: 0
      },
      campaigns: [],
      videoCount: 0
    }
  }
}

export default async function DashboardPage() {
  const { analytics, campaigns, videoCount } = await getDashboardData()

  const roas = analytics.avg_roas || 0
  const conversions = analytics.total_conversions || 0
  const spend = analytics.total_spend || 0
  const ctr = analytics.avg_ctr || 0

  return (
    <div className="p-4 sm:p-6 xl:px-8 xl:py-6 bg-black min-h-screen">
      <h1 className="text-xl sm:text-2xl font-semibold text-white mb-4 sm:mb-6">Dashboard</h1>

      <div className="mb-4 sm:mb-6">
        <PerformanceChart />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-4 sm:mb-6">
        <MetricCard 
          title="ROAS" 
          value={roas > 0 ? `${roas.toFixed(1)}x` : "0.0x"} 
          change={0} 
          changeLabel="vs last month" 
        />
        <MetricCard 
          title="Conversions" 
          value={conversions.toLocaleString()} 
          change={0} 
          changeLabel="vs last month" 
        />
        <MetricCard 
          title="Spend" 
          value={`$${spend.toLocaleString()}`} 
          change={0} 
          changeLabel="vs last month" 
        />
        <MetricCard 
          title="CTR" 
          value={`${(ctr * 100).toFixed(1)}%`} 
          change={0} 
          changeLabel="vs last month" 
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-4 sm:mb-6">
        <MetricCard 
          title="Videos Generated" 
          value={videoCount.toLocaleString()} 
          change={0} 
          changeLabel="total created" 
        />
        <MetricCard 
          title="Active Campaigns" 
          value={campaigns.filter(c => c.status === 'active').length.toString()} 
          change={0} 
          changeLabel="currently running" 
        />
        <MetricCard 
          title="Total Campaigns" 
          value={campaigns.length.toString()} 
          change={0} 
          changeLabel="all time" 
        />
        <MetricCard 
          title="Impressions" 
          value={analytics.total_impressions?.toLocaleString() || "0"} 
          change={0} 
          changeLabel="total reach" 
        />
      </div>

      <CampaignTable campaigns={campaigns} />
    </div>
  )
}
