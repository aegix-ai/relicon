"use client"

import { Card } from "@/components/ui/card"
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Area, AreaChart } from "recharts"
import { useEffect, useState } from "react"

interface ChartData {
  date: string
  roas: number
  conversions: number
  spend: number
}

export function PerformanceChart() {
  const [data, setData] = useState<ChartData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchChartData() {
      try {
        const response = await fetch('/api/analytics/chart-data')
        if (response.ok) {
          const chartData = await response.json()
          setData(chartData)
        } else {
          // Fallback to sample data if no real data
          setData([
            { date: "7 days ago", roas: 0, conversions: 0, spend: 0 },
            { date: "6 days ago", roas: 0, conversions: 0, spend: 0 },
            { date: "5 days ago", roas: 0, conversions: 0, spend: 0 },
            { date: "4 days ago", roas: 0, conversions: 0, spend: 0 },
            { date: "3 days ago", roas: 0, conversions: 0, spend: 0 },
            { date: "2 days ago", roas: 0, conversions: 0, spend: 0 },
            { date: "Yesterday", roas: 0, conversions: 0, spend: 0 },
            { date: "Today", roas: 0, conversions: 0, spend: 0 },
          ])
        }
      } catch (error) {
        console.error('Failed to fetch chart data:', error)
        // Use empty data as fallback
        setData([])
      } finally {
        setLoading(false)
      }
    }

    fetchChartData()
  }, [])

  if (loading) {
    return (
      <Card className="p-4 sm:p-6 bg-[#0f0f0f] border border-[#252525] rounded-xl shadow-2xl">
        <h3 className="text-sm sm:text-base font-medium text-white mb-3 sm:mb-4">Performance Overview</h3>
        <div className="h-64 sm:h-80 flex items-center justify-center">
          <p className="text-gray-400">Loading chart data...</p>
        </div>
      </Card>
    )
  }

  if (data.length === 0) {
    return (
      <Card className="p-4 sm:p-6 bg-[#0f0f0f] border border-[#252525] rounded-xl shadow-2xl">
        <h3 className="text-sm sm:text-base font-medium text-white mb-3 sm:mb-4">Performance Overview</h3>
        <div className="h-64 sm:h-80 flex items-center justify-center">
          <p className="text-gray-400">No performance data available yet. Start running campaigns to see analytics!</p>
        </div>
      </Card>
    )
  }

  return (
    <Card className="p-4 sm:p-6 bg-[#0f0f0f] border border-[#252525] rounded-xl shadow-2xl">
      <h3 className="text-sm sm:text-base font-medium text-white mb-3 sm:mb-4">Performance Overview</h3>
      <div className="h-64 sm:h-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
            <defs>
              <linearGradient id="roasGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#7c3aed" stopOpacity={0.05} />
              </linearGradient>
              <linearGradient id="conversionsGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#252525" />
            <XAxis 
              dataKey="date" 
              stroke="#666" 
              fontSize={10}
              tickLine={false}
              axisLine={false}
            />
            <YAxis 
              stroke="#666" 
              fontSize={10}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1f1f1f', 
                border: '1px solid #333',
                borderRadius: '8px',
                color: '#fff'
              }}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="roas"
              stroke="#7c3aed"
              fillOpacity={1}
              fill="url(#roasGradient)"
              strokeWidth={2}
              name="ROAS"
            />
            <Area
              type="monotone"
              dataKey="conversions"
              stroke="#10b981"
              fillOpacity={1}
              fill="url(#conversionsGradient)"
              strokeWidth={2}
              name="Conversions"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}
