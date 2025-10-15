import { Card } from "@/components/ui/card"
import { ArrowUp, ArrowDown } from "lucide-react"

interface MetricCardProps {
  title: string
  value: string
  change: number
  changeLabel: string
}

export function MetricCard({ title, value, change, changeLabel }: MetricCardProps) {
  const isPositive = change > 0

  return (
    <Card className="p-4 sm:p-6 bg-[#0f0f0f] border border-[#252525] rounded-xl shadow-lg hover:border-[#2f2f2f] transition-colors">
      <div className="space-y-1.5 sm:space-y-2">
        <p className="text-xs sm:text-sm font-medium text-gray-400">{title}</p>
        <p className="text-2xl sm:text-3xl font-bold text-white">{value}</p>
        <div className="flex items-center gap-1 flex-wrap">
          {isPositive ? (
            <ArrowUp className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-green-500" />
          ) : (
            <ArrowDown className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-red-500" />
          )}
          <span className={`text-xs sm:text-sm font-medium ${isPositive ? "text-green-500" : "text-red-500"}`}>
            {Math.abs(change)}%
          </span>
          <span className="text-xs sm:text-sm text-gray-500">{changeLabel}</span>
        </div>
      </div>
    </Card>
  )
}
