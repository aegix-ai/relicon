"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Eye,
  MousePointer,
  ShoppingCart,
  Target,
  BarChart3,
  PieChart,
  Activity,
  Download,
} from "lucide-react"

const performanceMetrics = [
  { title: "Total Revenue", value: "$32,040", change: "+28%", trend: "up", icon: DollarSign },
  { title: "Total Spend", value: "$8,420", change: "-5%", trend: "down", icon: Target },
  { title: "Overall ROAS", value: "3.8x", change: "+15%", trend: "up", icon: TrendingUp },
  { title: "Total Impressions", value: "2.4M", change: "+42%", trend: "up", icon: Eye },
  { title: "Total Clicks", value: "96.2K", change: "+31%", trend: "up", icon: MousePointer },
  { title: "Conversions", value: "3,240", change: "+18%", trend: "up", icon: ShoppingCart },
]

const platformPerformance = [
  { platform: "TikTok", revenue: "$14,200", roas: "4.2x", ctr: "4.8%", color: "bg-pink-500" },
  { platform: "Meta", revenue: "$12,840", roas: "3.6x", ctr: "3.2%", color: "bg-blue-500" },
  { platform: "YouTube", revenue: "$3,800", roas: "2.9x", ctr: "2.1%", color: "bg-red-500" },
  { platform: "Instagram", revenue: "$1,200", roas: "2.4x", ctr: "1.8%", color: "bg-purple-500" },
]

const topPerformingAds = [
  { name: "Skincare Routine TikTok", revenue: "$4,200", roas: "5.2x", impressions: "284K", platform: "TikTok" },
  { name: "Health Supplement Meta", revenue: "$3,800", roas: "4.8x", impressions: "192K", platform: "Meta" },
  { name: "Fitness App YouTube", revenue: "$2,400", roas: "3.9x", impressions: "156K", platform: "YouTube" },
  { name: "Fashion Brand Instagram", revenue: "$1,800", roas: "3.2x", impressions: "98K", platform: "Instagram" },
]

export default function PerformancePanel() {
  const [timeRange, setTimeRange] = useState("30d")
  const [animatedValues, setAnimatedValues] = useState<Record<string, number>>({})
  const [hoveredChart, setHoveredChart] = useState<{ x: number; y: number; value: string } | null>(null)

  // Animate revenue numbers
  useEffect(() => {
    const revenueValue = 32040
    let start = 0
    const duration = 2000
    const increment = revenueValue / (duration / 16)

    const timer = setInterval(() => {
      start += increment
      if (start >= revenueValue) {
        start = revenueValue
        clearInterval(timer)
      }
      setAnimatedValues((prev) => ({ ...prev, revenue: Math.floor(start) }))
    }, 16)

    return () => clearInterval(timer)
  }, [])

  return (
    <div className="p-6 space-y-8 bg-gray-900 dark:bg-gray-900 light:bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white dark:text-white light:text-gray-900 mb-2 flex items-center">
            <BarChart3 className="w-8 h-8 mr-3 text-[#FF5C00]" />
            Performance Analytics
          </h2>
          <p className="text-gray-300 dark:text-gray-300 light:text-gray-700">
            Comprehensive insights into your ad performance and ROI
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="bg-gray-700 dark:bg-gray-700 light:bg-white border-gray-600 dark:border-gray-600 light:border-gray-300 text-white dark:text-white light:text-gray-900 w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-gray-700 dark:bg-gray-700 light:bg-white border-gray-600 dark:border-gray-600 light:border-gray-300">
              <SelectItem
                value="7d"
                className="text-white dark:text-white light:text-gray-900 hover:bg-gray-600 dark:hover:bg-gray-600 light:hover:bg-gray-100"
              >
                Last 7 days
              </SelectItem>
              <SelectItem
                value="30d"
                className="text-white dark:text-white light:text-gray-900 hover:bg-gray-600 dark:hover:bg-gray-600 light:hover:bg-gray-100"
              >
                Last 30 days
              </SelectItem>
              <SelectItem
                value="90d"
                className="text-white dark:text-white light:text-gray-900 hover:bg-gray-600 dark:hover:bg-gray-600 light:hover:bg-gray-100"
              >
                Last 90 days
              </SelectItem>
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            className="border-gray-600 dark:border-gray-600 light:border-gray-300 text-gray-300 dark:text-gray-300 light:text-gray-700 hover:bg-gray-700 dark:hover:bg-gray-700 light:hover:bg-gray-100"
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Performance Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {performanceMetrics.map((metric) => {
          const Icon = metric.icon
          const TrendIcon = metric.trend === "up" ? TrendingUp : TrendingDown

          return (
            <div
              key={metric.title}
              className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 hover:border-[#FF5C00] transition-all duration-300 shadow-lg"
            >
              <div className="flex items-center justify-between mb-4">
                <Icon className="w-8 h-8 text-[#FF5C00]" />
                <div className={`flex items-center ${metric.trend === "up" ? "text-green-400" : "text-red-400"}`}>
                  <TrendIcon className="w-4 h-4 mr-1" />
                  <span className="text-sm font-medium">{metric.change}</span>
                </div>
              </div>
              <div className="text-2xl font-bold text-white dark:text-white light:text-gray-900 mb-1">
                {metric.title === "Total Revenue" && animatedValues.revenue
                  ? `$${animatedValues.revenue.toLocaleString()}`
                  : metric.value}
              </div>
              <div className="text-gray-400 dark:text-gray-400 light:text-gray-600 text-sm">{metric.title}</div>
            </div>
          )
        })}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Revenue Trend Chart */}
        <div className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
          <h3 className="text-xl font-semibold text-white dark:text-white light:text-gray-900 mb-6 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-[#FF5C00]" />
            Revenue Trend
          </h3>
          <div className="h-64 bg-gray-700 dark:bg-gray-700 light:bg-gray-100 rounded-lg p-4 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-green-500/10 to-[#FF5C00]/10"></div>
            <svg className="w-full h-full" viewBox="0 0 400 200">
              <defs>
                <linearGradient id="revenueGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#10B981" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#10B981" stopOpacity="0" />
                </linearGradient>
              </defs>
              {/* Revenue line */}
              <polyline
                fill="none"
                stroke="#10B981"
                strokeWidth="3"
                points="50,150 100,130 150,110 200,85 250,70 300,50 350,30"
              />
              <polygon
                fill="url(#revenueGradient)"
                points="50,150 100,130 150,110 200,85 250,70 300,50 350,30 350,180 50,180"
              />
              {/* Interactive data points */}
              {[
                { x: 50, y: 150, value: "$8.2K Revenue" },
                { x: 100, y: 130, value: "$12.4K Revenue" },
                { x: 150, y: 110, value: "$16.8K Revenue" },
                { x: 200, y: 85, value: "$22.1K Revenue" },
                { x: 250, y: 70, value: "$26.5K Revenue" },
                { x: 300, y: 50, value: "$29.8K Revenue" },
                { x: 350, y: 30, value: "$32.0K Revenue" },
              ].map((point, index) => (
                <circle
                  key={index}
                  cx={point.x}
                  cy={point.y}
                  r="6"
                  fill="#10B981"
                  className="cursor-pointer hover:r-8 transition-all"
                  onMouseEnter={(e) => {
                    const rect = e.currentTarget.getBoundingClientRect()
                    setHoveredChart({ x: rect.left, y: rect.top, value: point.value })
                  }}
                  onMouseLeave={() => setHoveredChart(null)}
                />
              ))}
            </svg>
            {hoveredChart && (
              <div
                className="absolute bg-gray-900 dark:bg-gray-900 light:bg-white text-white dark:text-white light:text-gray-900 px-2 py-1 rounded shadow-lg text-sm border border-gray-600 dark:border-gray-600 light:border-gray-300 z-10"
                style={{ left: hoveredChart.x - 200, top: hoveredChart.y - 100 }}
              >
                {hoveredChart.value}
              </div>
            )}
            <div className="absolute top-4 left-4 text-white dark:text-white light:text-gray-900 text-sm font-medium">
              Revenue Growth: +290%
            </div>
          </div>
          <div className="mt-4 grid grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-white dark:text-white light:text-gray-900">$8.2K</div>
              <div className="text-sm text-gray-400 dark:text-gray-400 light:text-gray-600">Week 1</div>
            </div>
            <div>
              <div className="text-lg font-bold text-white dark:text-white light:text-gray-900">$12.4K</div>
              <div className="text-sm text-gray-400 dark:text-gray-400 light:text-gray-600">Week 2</div>
            </div>
            <div>
              <div className="text-lg font-bold text-white dark:text-white light:text-gray-900">$18.6K</div>
              <div className="text-sm text-gray-400 dark:text-gray-400 light:text-gray-600">Week 3</div>
            </div>
            <div>
              <div className="text-lg font-bold text-white dark:text-white light:text-gray-900">$32.0K</div>
              <div className="text-sm text-gray-400 dark:text-gray-400 light:text-gray-600">Week 4</div>
            </div>
          </div>
        </div>

        {/* ROAS by Platform */}
        <div className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
          <h3 className="text-xl font-semibold text-white dark:text-white light:text-gray-900 mb-6 flex items-center">
            <PieChart className="w-5 h-5 mr-2 text-[#FF5C00]" />
            ROAS by Platform
          </h3>
          <div className="h-64 bg-gray-700 dark:bg-gray-700 light:bg-gray-100 rounded-lg p-4 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10"></div>
            <svg className="w-full h-full" viewBox="0 0 200 200">
              {/* Interactive pie chart segments */}
              <circle
                cx="100"
                cy="100"
                r="80"
                fill="none"
                stroke="#EC4899"
                strokeWidth="20"
                strokeDasharray="125.6 314"
                transform="rotate(-90 100 100)"
                className="cursor-pointer hover:stroke-width-25 transition-all"
                onMouseEnter={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect()
                  setHoveredChart({ x: rect.left, y: rect.top, value: "TikTok: 4.2x ROAS" })
                }}
                onMouseLeave={() => setHoveredChart(null)}
              />
              <circle
                cx="100"
                cy="100"
                r="80"
                fill="none"
                stroke="#3B82F6"
                strokeWidth="20"
                strokeDasharray="100.5 314"
                strokeDashoffset="-125.6"
                transform="rotate(-90 100 100)"
                className="cursor-pointer hover:stroke-width-25 transition-all"
                onMouseEnter={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect()
                  setHoveredChart({ x: rect.left, y: rect.top, value: "Meta: 3.6x ROAS" })
                }}
                onMouseLeave={() => setHoveredChart(null)}
              />
              <circle
                cx="100"
                cy="100"
                r="80"
                fill="none"
                stroke="#EF4444"
                strokeWidth="20"
                strokeDasharray="62.8 314"
                strokeDashoffset="-226.1"
                transform="rotate(-90 100 100)"
                className="cursor-pointer hover:stroke-width-25 transition-all"
                onMouseEnter={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect()
                  setHoveredChart({ x: rect.left, y: rect.top, value: "YouTube: 2.9x ROAS" })
                }}
                onMouseLeave={() => setHoveredChart(null)}
              />
              <circle
                cx="100"
                cy="100"
                r="80"
                fill="none"
                stroke="#8B5CF6"
                strokeWidth="20"
                strokeDasharray="25.1 314"
                strokeDashoffset="-288.9"
                transform="rotate(-90 100 100)"
                className="cursor-pointer hover:stroke-width-25 transition-all"
                onMouseEnter={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect()
                  setHoveredChart({ x: rect.left, y: rect.top, value: "Instagram: 2.4x ROAS" })
                }}
                onMouseLeave={() => setHoveredChart(null)}
              />
            </svg>
            {hoveredChart && (
              <div
                className="absolute bg-gray-900 dark:bg-gray-900 light:bg-white text-white dark:text-white light:text-gray-900 px-2 py-1 rounded shadow-lg text-sm border border-gray-600 dark:border-gray-600 light:border-gray-300 z-10"
                style={{ left: hoveredChart.x - 200, top: hoveredChart.y - 100 }}
              >
                {hoveredChart.value}
              </div>
            )}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="text-2xl font-bold text-white dark:text-white light:text-gray-900">3.8x</div>
                <div className="text-sm text-gray-400 dark:text-gray-400 light:text-gray-600">Avg ROAS</div>
              </div>
            </div>
          </div>
          <div className="mt-4 space-y-2">
            {platformPerformance.map((platform) => (
              <div key={platform.platform} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className={`w-3 h-3 rounded-full ${platform.color} mr-2`}></div>
                  <span className="text-gray-300 dark:text-gray-300 light:text-gray-700">{platform.platform}</span>
                </div>
                <span className="text-white dark:text-white light:text-gray-900 font-medium">{platform.roas}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Platform Performance Breakdown */}
      <div className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
        <h3 className="text-xl font-semibold text-white dark:text-white light:text-gray-900 mb-6 flex items-center">
          <Target className="w-5 h-5 mr-2 text-[#FF5C00]" />
          Platform Performance Breakdown
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {platformPerformance.map((platform) => (
            <div
              key={platform.platform}
              className="bg-gray-700 dark:bg-gray-700 light:bg-gray-100 rounded-lg p-4 hover:bg-gray-600 dark:hover:bg-gray-600 light:hover:bg-gray-200 transition-colors"
            >
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-semibold text-white dark:text-white light:text-gray-900">{platform.platform}</h4>
                <div className={`w-3 h-3 rounded-full ${platform.color}`}></div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400 dark:text-gray-400 light:text-gray-600 text-sm">Revenue</span>
                  <span className="text-white dark:text-white light:text-gray-900 font-medium">{platform.revenue}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400 dark:text-gray-400 light:text-gray-600 text-sm">ROAS</span>
                  <span className="text-green-400 font-medium">{platform.roas}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400 dark:text-gray-400 light:text-gray-600 text-sm">CTR</span>
                  <span className="text-blue-400 font-medium">{platform.ctr}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Top Performing Ads */}
      <div className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
        <h3 className="text-xl font-semibold text-white dark:text-white light:text-gray-900 mb-6 flex items-center">
          <Activity className="w-5 h-5 mr-2 text-[#FF5C00]" />
          Top Performing Ads
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700 dark:border-gray-700 light:border-gray-200">
                <th className="text-left text-gray-400 dark:text-gray-400 light:text-gray-600 font-medium py-3">
                  Ad Name
                </th>
                <th className="text-left text-gray-400 dark:text-gray-400 light:text-gray-600 font-medium py-3">
                  Platform
                </th>
                <th className="text-left text-gray-400 dark:text-gray-400 light:text-gray-600 font-medium py-3">
                  Revenue
                </th>
                <th className="text-left text-gray-400 dark:text-gray-400 light:text-gray-600 font-medium py-3">
                  ROAS
                </th>
                <th className="text-left text-gray-400 dark:text-gray-400 light:text-gray-600 font-medium py-3">
                  Impressions
                </th>
                <th className="text-left text-gray-400 dark:text-gray-400 light:text-gray-600 font-medium py-3">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {topPerformingAds.map((ad, index) => (
                <tr
                  key={index}
                  className="border-b border-gray-700 dark:border-gray-700 light:border-gray-200 hover:bg-gray-700 dark:hover:bg-gray-700 light:hover:bg-gray-100 transition-colors"
                >
                  <td className="py-4 text-white dark:text-white light:text-gray-900 font-medium">{ad.name}</td>
                  <td className="py-4">
                    <span className="px-2 py-1 bg-gray-600 dark:bg-gray-600 light:bg-gray-200 text-gray-300 dark:text-gray-300 light:text-gray-700 rounded text-sm">
                      {ad.platform}
                    </span>
                  </td>
                  <td className="py-4 text-green-400 font-medium">{ad.revenue}</td>
                  <td className="py-4 text-[#FF5C00] font-medium">{ad.roas}</td>
                  <td className="py-4 text-gray-300 dark:text-gray-300 light:text-gray-700">{ad.impressions}</td>
                  <td className="py-4">
                    <Button
                      size="sm"
                      variant="outline"
                      className="border-gray-600 dark:border-gray-600 light:border-gray-300 text-gray-300 dark:text-gray-300 light:text-gray-700 hover:bg-gray-600 dark:hover:bg-gray-600 light:hover:bg-gray-200"
                    >
                      View Details
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* AI Insights */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-700 dark:from-gray-800 dark:to-gray-700 light:from-gray-100 light:to-gray-200 rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
        <h3 className="text-xl font-semibold text-white dark:text-white light:text-gray-900 mb-6 flex items-center">
          <Activity className="w-5 h-5 mr-2 text-[#FF5C00]" />
          AI Performance Insights
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-gray-700 dark:bg-gray-700 light:bg-gray-300 rounded-lg p-4">
            <h4 className="text-[#FF5C00] font-semibold mb-2">🎯 Best Performing Hook</h4>
            <p className="text-gray-300 dark:text-gray-300 light:text-gray-700 text-sm">
              "Are you tired of..." hooks are generating 34% higher CTR than other variations
            </p>
          </div>
          <div className="bg-gray-700 dark:bg-gray-700 light:bg-gray-300 rounded-lg p-4">
            <h4 className="text-[#FF5C00] font-semibold mb-2">📱 Platform Optimization</h4>
            <p className="text-gray-300 dark:text-gray-300 light:text-gray-700 text-sm">
              TikTok ads perform 42% better with vertical 9:16 format and 15-second duration
            </p>
          </div>
          <div className="bg-gray-700 dark:bg-gray-700 light:bg-gray-300 rounded-lg p-4">
            <h4 className="text-[#FF5C00] font-semibold mb-2">⏰ Timing Insights</h4>
            <p className="text-gray-300 dark:text-gray-300 light:text-gray-700 text-sm">
              Your audience is most active between 7-9 PM EST, showing 28% higher engagement
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
