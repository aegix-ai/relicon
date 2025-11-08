"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  TrendingUp,
  DollarSign,
  Eye,
  MousePointerClick,
  ShoppingCart,
  RefreshCw,
  Instagram,
  Facebook,
  Music2,
  ArrowUp,
  ArrowDown
} from "lucide-react"
import { toast } from "sonner"

interface MetricCardData {
  title: string
  value: string | number
  change: number
  icon: React.ReactNode
  trend: 'up' | 'down' | 'neutral'
}

interface Campaign {
  id: number
  name: string
  status: string
  total_impressions: number
  total_reach: number
  avg_ctr: number
  avg_roas: number
  total_conversions: number
  spend_total: number
  budget_total: number
  total_posts: number
}

export default function AnalyticsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [metrics, setMetrics] = useState<MetricCardData[]>([])
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [timeRange, setTimeRange] = useState("7d")

  // TODO: Get user ID from authentication
  const userId = null // Replace with auth.user?.id when auth is implemented

  useEffect(() => {
    fetchData()
  }, [timeRange])

  const fetchData = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/campaigns?userId=${userId}`)
      const data = await response.json()
      setCampaigns(data.campaigns || [])

      // Calculate aggregate metrics
      calculateMetrics(data.campaigns || [])
    } catch (error) {
      console.error('Error fetching analytics:', error)
      toast.error('Failed to load analytics')
    } finally {
      setLoading(false)
    }
  }

  const calculateMetrics = (campaignsData: Campaign[]) => {
    const totalImpressions = campaignsData.reduce((sum, c) => sum + (c.total_impressions || 0), 0)
    const totalReach = campaignsData.reduce((sum, c) => sum + (c.total_reach || 0), 0)
    const totalConversions = campaignsData.reduce((sum, c) => sum + (c.total_conversions || 0), 0)
    const totalSpend = campaignsData.reduce((sum, c) => sum + (c.spend_total || 0), 0)
    const totalRevenue = campaignsData.reduce((sum, c) => sum + ((c.total_conversions || 0) * 50), 0) // Assuming $50 per conversion
    const avgCTR = campaignsData.length > 0
      ? campaignsData.reduce((sum, c) => sum + (c.avg_ctr || 0), 0) / campaignsData.length
      : 0
    const avgROAS = campaignsData.length > 0
      ? campaignsData.reduce((sum, c) => sum + (c.avg_roas || 0), 0) / campaignsData.length
      : 0

    setMetrics([
      {
        title: "Total Reach",
        value: totalReach.toLocaleString(),
        change: 12.5,
        icon: <Eye className="w-5 h-5" />,
        trend: "up"
      },
      {
        title: "CTR",
        value: `${avgCTR.toFixed(2)}%`,
        change: 3.2,
        icon: <MousePointerClick className="w-5 h-5" />,
        trend: "up"
      },
      {
        title: "ROAS",
        value: `${avgROAS.toFixed(0)}%`,
        change: 8.1,
        icon: <TrendingUp className="w-5 h-5" />,
        trend: "up"
      },
      {
        title: "Conversions",
        value: totalConversions,
        change: -2.4,
        icon: <ShoppingCart className="w-5 h-5" />,
        trend: totalConversions > 0 ? "up" : "neutral"
      }
    ])
  }

  const syncAnalytics = async () => {
    setSyncing(true)
    try {
      const response = await fetch('/api/social/analytics/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId })
      })

      const data = await response.json()

      if (data.success) {
        toast.success(`Synced ${data.synced} posts`, {
          description: data.errors > 0 ? `${data.errors} errors occurred` : 'All metrics up to date'
        })
        fetchData()
      } else {
        toast.error('Sync failed')
      }
    } catch (error) {
      console.error('Sync error:', error)
      toast.error('Failed to sync analytics')
    } finally {
      setSyncing(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500/20 text-green-400'
      case 'paused':
        return 'bg-yellow-500/20 text-yellow-400'
      case 'completed':
        return 'bg-blue-500/20 text-blue-400'
      default:
        return 'bg-gray-500/20 text-gray-400'
    }
  }

  const getPlatformIcon = (platforms: string[]) => {
    if (!platforms || platforms.length === 0) return null

    return (
      <div className="flex gap-1">
        {platforms.includes('instagram') && <Instagram className="w-4 h-4" />}
        {platforms.includes('facebook') && <Facebook className="w-4 h-4" />}
        {platforms.includes('tiktok') && <Music2 className="w-4 h-4" />}
      </div>
    )
  }

  return (
    <div className="p-4 sm:p-6 xl:px-8 xl:py-6 bg-[#0a0a0a] min-h-screen">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-white mb-1">Analytics</h1>
          <p className="text-gray-400 text-sm">Track your campaign performance and ROI</p>
        </div>

        <div className="flex items-center gap-3">
          {/* Time Range Selector */}
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-32 bg-[#0f0f0f] border-[#252525] text-white">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-[#0f0f0f] border-[#252525] text-white">
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
              <SelectItem value="all">All time</SelectItem>
            </SelectContent>
          </Select>

          {/* Sync Button */}
          <Button
            onClick={syncAnalytics}
            disabled={syncing}
            className="bg-white text-black hover:bg-gray-200"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing...' : 'Sync Metrics'}
          </Button>
        </div>
      </div>

      {/* Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {metrics.map((metric, index) => (
          <Card key={index} className="p-5 bg-[#0f0f0f] border-[#252525]">
            <div className="flex items-start justify-between mb-3">
              <div className="p-2 bg-white/5 rounded-lg">
                {metric.icon}
              </div>
              <div className={`flex items-center gap-1 text-xs ${
                metric.trend === 'up' ? 'text-green-400' :
                metric.trend === 'down' ? 'text-red-400' :
                'text-gray-400'
              }`}>
                {metric.trend === 'up' ? <ArrowUp className="w-3 h-3" /> :
                 metric.trend === 'down' ? <ArrowDown className="w-3 h-3" /> : null}
                {Math.abs(metric.change)}%
              </div>
            </div>
            <p className="text-gray-400 text-sm mb-1">{metric.title}</p>
            <p className="text-2xl font-semibold text-white">{metric.value}</p>
          </Card>
        ))}
      </div>

      {/* Campaigns Table */}
      <Card className="p-6 bg-[#0f0f0f] border-[#252525]">
        <h2 className="text-lg font-semibold text-white mb-4">Campaigns</h2>

        {loading ? (
          <div className="text-center py-12">
            <RefreshCw className="w-8 h-8 text-gray-400 animate-spin mx-auto mb-3" />
            <p className="text-gray-400">Loading campaigns...</p>
          </div>
        ) : campaigns.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-400 mb-2">No campaigns yet</p>
            <p className="text-gray-500 text-sm">Create a campaign to start tracking performance</p>
            <Button
              onClick={() => window.location.href = '/dashboard/campaigns'}
              className="mt-4 bg-white text-black hover:bg-gray-200"
            >
              Create Campaign
            </Button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#252525]">
                  <th className="text-left text-gray-400 font-medium text-sm py-3 px-2">Campaign</th>
                  <th className="text-left text-gray-400 font-medium text-sm py-3 px-2">Status</th>
                  <th className="text-right text-gray-400 font-medium text-sm py-3 px-2">Impressions</th>
                  <th className="text-right text-gray-400 font-medium text-sm py-3 px-2">CTR</th>
                  <th className="text-right text-gray-400 font-medium text-sm py-3 px-2">Conversions</th>
                  <th className="text-right text-gray-400 font-medium text-sm py-3 px-2">Spend</th>
                  <th className="text-right text-gray-400 font-medium text-sm py-3 px-2">ROAS</th>
                </tr>
              </thead>
              <tbody>
                {campaigns.map((campaign) => (
                  <tr
                    key={campaign.id}
                    className="border-b border-[#252525] hover:bg-[#0a0a0a] cursor-pointer transition-colors"
                    onClick={() => window.location.href = `/dashboard/campaigns/${campaign.id}`}
                  >
                    <td className="py-4 px-2">
                      <div>
                        <p className="text-white font-medium">{campaign.name}</p>
                        <p className="text-gray-400 text-xs mt-1">{campaign.total_posts} posts</p>
                      </div>
                    </td>
                    <td className="py-4 px-2">
                      <Badge className={`capitalize ${getStatusColor(campaign.status)}`}>
                        {campaign.status}
                      </Badge>
                    </td>
                    <td className="py-4 px-2 text-right text-white">
                      {campaign.total_impressions?.toLocaleString() || 0}
                    </td>
                    <td className="py-4 px-2 text-right text-white">
                      {campaign.avg_ctr?.toFixed(2) || 0}%
                    </td>
                    <td className="py-4 px-2 text-right text-white">
                      {campaign.total_conversions || 0}
                    </td>
                    <td className="py-4 px-2 text-right text-white">
                      ${campaign.spend_total?.toFixed(2) || 0}
                    </td>
                    <td className="py-4 px-2 text-right">
                      <span className={`font-semibold ${
                        (campaign.avg_roas || 0) > 100 ? 'text-green-400' :
                        (campaign.avg_roas || 0) > 0 ? 'text-yellow-400' :
                        'text-red-400'
                      }`}>
                        {campaign.avg_roas?.toFixed(0) || 0}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Info Box */}
      {campaigns.length > 0 && (
        <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
          <p className="text-blue-400 text-sm">
            💡 <strong>ROAS (Return on Ad Spend)</strong>: For every $1 spent, a 200% ROAS means you earned $2 back.
            Higher is better!
          </p>
        </div>
      )}
    </div>
  )
}
