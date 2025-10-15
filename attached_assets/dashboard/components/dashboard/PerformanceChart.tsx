"use client"

import { Card } from "@/components/ui/card"
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Area, AreaChart } from "recharts"

const data = [
  { month: "Jan", roas: 2.8, performance: 55 },
  { month: "Feb", roas: 3.2, performance: 62 },
  { month: "Mar", roas: 2.5, performance: 68 },
  { month: "Apr", roas: 4.1, performance: 74 },
  { month: "May", roas: 3.6, performance: 80 },
  { month: "Jun", roas: 4.8, performance: 86 },
  { month: "Jul", roas: 4.2, performance: 92 },
  { month: "Aug", roas: 5.3, performance: 98 },
  { month: "Sep", roas: 4.7, performance: 104 },
  { month: "Oct", roas: 5.8, performance: 110 },
]

export function PerformanceChart() {
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
              <linearGradient id="performanceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.05} />
              </linearGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                <feMerge>
                  <feMergeNode in="coloredBlur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f1f1f" />
            <XAxis dataKey="month" stroke="#6b7280" style={{ fontSize: "10px" }} tick={{ fontSize: 10 }} />
            <YAxis yAxisId="left" stroke="#7c3aed" style={{ fontSize: "10px" }} tick={{ fontSize: 10 }} />
            <YAxis
              yAxisId="right"
              orientation="right"
              stroke="#06b6d4"
              style={{ fontSize: "10px" }}
              tick={{ fontSize: 10 }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0a0a0a",
                border: "1px solid #252525",
                borderRadius: "8px",
                color: "#ffffff",
                fontSize: "12px",
              }}
            />
            <Legend wrapperStyle={{ color: "#9ca3af", fontSize: "11px" }} />
            <Area
              yAxisId="left"
              type="monotone"
              dataKey="roas"
              stroke="#7c3aed"
              strokeWidth={2}
              fill="url(#roasGradient)"
              name="ROAS"
              dot={{ fill: "#7c3aed", r: 3, strokeWidth: 2, stroke: "#0a0a0a" }}
            />
            <Area
              yAxisId="right"
              type="monotone"
              dataKey="performance"
              stroke="#06b6d4"
              strokeWidth={2}
              fill="url(#performanceGradient)"
              name="Ads Performance"
              dot={{ fill: "#06b6d4", r: 3, strokeWidth: 2, stroke: "#0a0a0a" }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}
