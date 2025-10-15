import { MetricCard } from "@/components/dashboard/MetricCard"
import { PerformanceChart } from "@/components/dashboard/PerformanceChart"
import { CampaignTable } from "@/components/dashboard/CampaignTable"

export default function DashboardPage() {
  return (
    <div className="p-4 sm:p-6 xl:px-8 xl:py-6 bg-black min-h-screen">
      <h1 className="text-xl sm:text-2xl font-semibold text-white mb-4 sm:mb-6">Dashboard</h1>

      <div className="mb-4 sm:mb-6">
        <PerformanceChart />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-4 sm:mb-6">
        <MetricCard title="ROAS" value="4.2x" change={12.5} changeLabel="vs last month" />
        <MetricCard title="Conversions" value="1,247" change={8.3} changeLabel="vs last month" />
        <MetricCard title="Spend" value="$8,660" change={-3.2} changeLabel="vs last month" />
        <MetricCard title="CTR" value="6.8%" change={5.7} changeLabel="vs last month" />
      </div>

      <CampaignTable />
    </div>
  )
}
