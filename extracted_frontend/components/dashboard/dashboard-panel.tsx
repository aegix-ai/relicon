"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import {
  Target,
  DollarSign,
  ShoppingCart,
  TrendingUp,
  Brain,
  Plus,
  Link,
  Play,
  Copy,
  Zap,
  Activity,
} from "lucide-react"

const summaryCards = [
  { title: "Total Ads Generated", value: 158, icon: Target, color: "text-blue-500", trend: "+12%" },
  { title: "Total Spend", value: "$8,420", icon: DollarSign, color: "text-red-500", trend: "-5%" },
  { title: "Total Revenue", value: "$32,040", icon: ShoppingCart, color: "text-green-500", trend: "+28%" },
  { title: "Average ROAS", value: "3.8x", icon: TrendingUp, color: "text-orange-500", trend: "+15%" },
]

const bestPerformingAd = {
  thumbnail: "/placeholder.svg?height=200&width=300",
  title: "Skincare Routine Ad",
  roas: "4.2x",
  views: "284K",
  clicks: "12.4K",
  ctr: "4.37%",
}

export default function DashboardPanel() {
  const [animatedValues, setAnimatedValues] = useState<Record<string, number>>({})
  const [chartPeriod, setChartPeriod] = useState("7d")
  const [hoveredPoint, setHoveredPoint] = useState<{ x: number; y: number; value: string } | null>(null)

  // Animate numbers on mount
  useEffect(() => {
    summaryCards.forEach((card) => {
      if (typeof card.value === "number") {
        let start = 0
        const end = card.value
        const duration = 2000
        const increment = end / (duration / 16)

        const timer = setInterval(() => {
          start += increment
          if (start >= end) {
            start = end
            clearInterval(timer)
          }
          setAnimatedValues((prev) => ({ ...prev, [card.title]: Math.floor(start) }))
        }, 16)
      }
    })
  }, [])

  return (
    <div className="p-6 space-y-8 bg-gray-900 dark:bg-gray-900 light:bg-gray-50 min-h-screen">
      {/* Top Summary Cards (KPIs) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {summaryCards.map((card) => {
          const Icon = card.icon
          const displayValue = typeof card.value === "number" ? animatedValues[card.title] || 0 : card.value

          return (
            <div
              key={card.title}
              className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 hover:border-[#FF5C00] transition-all duration-300 group shadow-lg"
            >
              <div className="flex items-center justify-between mb-4">
                <Icon className={`w-8 h-8 ${card.color} group-hover:scale-110 transition-transform duration-300`} />
                <div className="text-right">
                  <div className="text-2xl font-bold text-white dark:text-white light:text-gray-900">
                    {typeof card.value === "number" ? displayValue.toLocaleString() : displayValue}
                  </div>
                  <div
                    className={`text-sm font-medium ${card.trend.startsWith("+") ? "text-green-400" : "text-red-400"}`}
                  >
                    {card.trend}
                  </div>
                </div>
              </div>
              <h3 className="text-gray-400 dark:text-gray-400 light:text-gray-600 text-sm font-medium">{card.title}</h3>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Trend Chart */}
        <div className="lg:col-span-2 bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-white dark:text-white light:text-gray-900 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2 text-[#FF5C00]" />
              ROAS Over Time
            </h3>
            <div className="flex space-x-2">
              <Button
                size="sm"
                variant={chartPeriod === "7d" ? "default" : "outline"}
                onClick={() => setChartPeriod("7d")}
                className={
                  chartPeriod === "7d"
                    ? "bg-[#FF5C00] hover:bg-[#E05000]"
                    : "border-gray-600 dark:border-gray-600 light:border-gray-300 text-gray-300 dark:text-gray-300 light:text-gray-700"
                }
              >
                7D
              </Button>
              <Button
                size="sm"
                variant={chartPeriod === "30d" ? "default" : "outline"}
                onClick={() => setChartPeriod("30d")}
                className={
                  chartPeriod === "30d"
                    ? "bg-[#FF5C00] hover:bg-[#E05000]"
                    : "border-gray-600 dark:border-gray-600 light:border-gray-300 text-gray-300 dark:text-gray-300 light:text-gray-700"
                }
              >
                30D
              </Button>
            </div>
          </div>
          <div className="h-64 bg-gray-700 dark:bg-gray-700 light:bg-gray-100 rounded-lg p-4 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-[#FF5C00]/10 to-transparent"></div>
            <svg className="w-full h-full" viewBox="0 0 400 200">
              <defs>
                <linearGradient id="roasGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#FF5C00" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#FF5C00" stopOpacity="0" />
                </linearGradient>
              </defs>
              <polyline
                fill="none"
                stroke="#FF5C00"
                strokeWidth="3"
                points="20,160 80,140 140,120 200,100 260,80 320,60 380,40"
              />
              <polygon
                fill="url(#roasGradient)"
                points="20,160 80,140 140,120 200,100 260,80 320,60 380,40 380,180 20,180"
              />
              {/* Interactive data points */}
              {[
                { x: 20, y: 160, value: "2.1x ROAS" },
                { x: 80, y: 140, value: "2.4x ROAS" },
                { x: 140, y: 120, value: "2.8x ROAS" },
                { x: 200, y: 100, value: "3.2x ROAS" },
                { x: 260, y: 80, value: "3.6x ROAS" },
                { x: 320, y: 60, value: "4.0x ROAS" },
                { x: 380, y: 40, value: "4.2x ROAS" },
              ].map((point, index) => (
                <circle
                  key={index}
                  cx={point.x}
                  cy={point.y}
                  r="6"
                  fill="#FF5C00"
                  className="cursor-pointer hover:r-8 transition-all"
                  onMouseEnter={(e) => {
                    const rect = e.currentTarget.getBoundingClientRect()
                    setHoveredPoint({ x: rect.left, y: rect.top, value: point.value })
                  }}
                  onMouseLeave={() => setHoveredPoint(null)}
                />
              ))}
            </svg>
            {hoveredPoint && (
              <div
                className="absolute bg-gray-900 dark:bg-gray-900 light:bg-white text-white dark:text-white light:text-gray-900 px-2 py-1 rounded shadow-lg text-sm border border-gray-600 dark:border-gray-600 light:border-gray-300"
                style={{ left: hoveredPoint.x - 200, top: hoveredPoint.y - 100 }}
              >
                {hoveredPoint.value}
              </div>
            )}
            <div className="absolute top-4 left-4 text-white dark:text-white light:text-gray-900 text-sm font-medium">
              ROAS Improvement: +47%
            </div>
          </div>
          <div className="mt-4 grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-white dark:text-white light:text-gray-900">2.8x</div>
              <div className="text-sm text-gray-400 dark:text-gray-400 light:text-gray-600">Week 1</div>
              <div className="text-xs text-red-400">-12%</div>
            </div>
            <div>
              <div className="text-lg font-bold text-white dark:text-white light:text-gray-900">3.4x</div>
              <div className="text-sm text-gray-400 dark:text-gray-400 light:text-gray-600">Week 2</div>
              <div className="text-xs text-green-400">+21%</div>
            </div>
            <div>
              <div className="text-lg font-bold text-white dark:text-white light:text-gray-900">4.1x</div>
              <div className="text-sm text-gray-400 dark:text-gray-400 light:text-gray-600">Week 3</div>
              <div className="text-xs text-green-400">+47%</div>
            </div>
          </div>
        </div>

        {/* Best Performing Ad */}
        <div className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
          <h3 className="text-xl font-semibold text-white dark:text-white light:text-gray-900 mb-6 flex items-center">
            <Play className="w-5 h-5 mr-2 text-[#FF5C00]" />
            Best Performing Ad
          </h3>
          <div className="space-y-4">
            {/* Vertical aspect ratio for mobile ads - smaller size */}
            <div className="aspect-[9/20] bg-gray-700 dark:bg-gray-700 light:bg-gray-200 rounded-lg flex items-center justify-center border border-gray-600 dark:border-gray-600 light:border-gray-300 relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-br from-[#FF5C00]/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <img
                src="/placeholder.svg?height=400&width=225"
                alt="Ad Preview"
                className="w-full h-full object-cover rounded-lg"
              />
              <div className="absolute inset-0 flex items-center justify-center">
                <Play className="w-12 h-12 text-white drop-shadow-lg group-hover:scale-110 transition-transform duration-300" />
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-white dark:text-white light:text-gray-900 mb-2">
                {bestPerformingAd.title}
              </h4>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span className="text-gray-400 dark:text-gray-400 light:text-gray-600">ROAS:</span>
                  <span className="text-green-400 font-bold ml-2">{bestPerformingAd.roas}</span>
                </div>
                <div>
                  <span className="text-gray-400 dark:text-gray-400 light:text-gray-600">CTR:</span>
                  <span className="text-blue-400 font-bold ml-2">{bestPerformingAd.ctr}</span>
                </div>
                <div>
                  <span className="text-gray-400 dark:text-gray-400 light:text-gray-600">Views:</span>
                  <span className="text-white dark:text-white light:text-gray-900 font-bold ml-2">
                    {bestPerformingAd.views}
                  </span>
                </div>
                <div>
                  <span className="text-gray-400 dark:text-gray-400 light:text-gray-600">Clicks:</span>
                  <span className="text-white dark:text-white light:text-gray-900 font-bold ml-2">
                    {bestPerformingAd.clicks}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex space-x-2">
              <Button size="sm" className="flex-1 bg-[#FF5C00] hover:bg-[#E05000] text-white">
                <Copy className="w-4 h-4 mr-1" />
                Replicate
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="flex-1 border-gray-600 dark:border-gray-600 light:border-gray-300 text-gray-300 dark:text-gray-300 light:text-gray-700"
              >
                Details
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Rest of the component with similar light theme updates... */}
      {/* AI Engine Status & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* AI Engine Status */}
        <div className="bg-gradient-to-r from-gray-800 to-gray-700 dark:from-gray-800 dark:to-gray-700 light:from-gray-100 light:to-gray-200 rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
          <h3 className="text-xl font-semibold text-white dark:text-white light:text-gray-900 mb-4 flex items-center">
            <Brain className="w-5 h-5 mr-2 text-[#FF5C00]" />
            AI Engine Status
          </h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-green-400 font-medium">Active Learning Mode</span>
            </div>
            <p className="text-gray-300 dark:text-gray-300 light:text-gray-700">
              Currently optimizing hook durations under 5s for TikTok CTR improvement. Testing 12 variations across 3
              audience segments.
            </p>
            <div className="bg-gray-700 dark:bg-gray-700 light:bg-gray-300 rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-400 dark:text-gray-400 light:text-gray-600">Learning Progress</span>
                <span className="text-sm text-[#FF5C00] font-medium">73%</span>
              </div>
              <div className="w-full bg-gray-600 dark:bg-gray-600 light:bg-gray-400 rounded-full h-2">
                <div className="bg-[#FF5C00] h-2 rounded-full w-3/4 transition-all duration-1000"></div>
              </div>
            </div>
            <div className="text-sm text-gray-400 dark:text-gray-400 light:text-gray-600">
              <div className="flex justify-between">
                <span>Next optimization cycle:</span>
                <span className="text-[#FF5C00] font-medium">2 days</span>
              </div>
              <div className="flex justify-between">
                <span>Models trained today:</span>
                <span className="text-green-400 font-medium">8</span>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
          <h3 className="text-xl font-semibold text-white dark:text-white light:text-gray-900 mb-6 flex items-center">
            <Zap className="w-5 h-5 mr-2 text-[#FF5C00]" />
            Quick Actions
          </h3>
          <div className="space-y-4">
            <Button className="w-full bg-[#FF5C00] hover:bg-[#E05000] text-white py-4 text-lg font-semibold rounded-lg transition-all duration-300 hover:shadow-lg">
              <Plus className="w-5 h-5 mr-2" />
              Create New Ad
            </Button>
            <Button
              variant="outline"
              className="w-full border-gray-600 dark:border-gray-600 light:border-gray-300 text-gray-300 dark:text-gray-300 light:text-gray-700 hover:bg-gray-700 dark:hover:bg-gray-700 light:hover:bg-gray-100 py-4 text-lg font-semibold rounded-lg transition-all duration-300"
            >
              <Link className="w-5 h-5 mr-2" />
              Connect Account
            </Button>
            <div className="grid grid-cols-2 gap-4">
              <Button
                variant="outline"
                className="border-gray-600 dark:border-gray-600 light:border-gray-300 text-gray-300 dark:text-gray-300 light:text-gray-700 hover:bg-gray-700 dark:hover:bg-gray-700 light:hover:bg-gray-100 py-3 transition-all duration-300"
              >
                <Activity className="w-4 h-4 mr-2" />
                Analytics
              </Button>
              <Button
                variant="outline"
                className="border-gray-600 dark:border-gray-600 light:border-gray-300 text-gray-300 dark:text-gray-300 light:text-gray-700 hover:bg-gray-700 dark:hover:bg-gray-700 light:hover:bg-gray-100 py-3 transition-all duration-300"
              >
                <Target className="w-4 h-4 mr-2" />
                Campaigns
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
        <h3 className="text-xl font-semibold text-white dark:text-white light:text-gray-900 mb-6 flex items-center">
          <Activity className="w-5 h-5 mr-2 text-[#FF5C00]" />
          Recent AI Activity
        </h3>
        <div className="space-y-4">
          {[
            { time: "2 hours ago", action: "Generated 3 new ad variations for TikTok campaign", status: "success" },
            {
              time: "5 hours ago",
              action: "Optimized targeting for Meta ads - CTR improved by 23%",
              status: "success",
            },
            { time: "1 day ago", action: "A/B tested hook variations - identified winning formula", status: "success" },
            { time: "2 days ago", action: "Connected new audience segment - analyzing performance", status: "pending" },
          ].map((activity, index) => (
            <div
              key={index}
              className="flex items-start space-x-4 p-4 bg-gray-700 dark:bg-gray-700 light:bg-gray-100 rounded-lg"
            >
              <div
                className={`w-3 h-3 rounded-full mt-2 ${
                  activity.status === "success" ? "bg-green-500" : "bg-yellow-500 animate-pulse"
                }`}
              ></div>
              <div className="flex-1">
                <p className="text-white dark:text-white light:text-gray-900">{activity.action}</p>
                <p className="text-sm text-gray-400 dark:text-gray-400 light:text-gray-600">{activity.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
