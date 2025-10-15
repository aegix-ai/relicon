import { Card } from "@/components/ui/card"

const campaigns = [
  { name: "Summer Sale 2024", impressions: "125K", clicks: "8.5K", ctr: "6.8%", spend: "$2,450" },
  { name: "Product Launch", impressions: "98K", clicks: "6.2K", ctr: "6.3%", spend: "$1,890" },
  { name: "Brand Awareness", impressions: "210K", clicks: "12.1K", ctr: "5.8%", spend: "$3,200" },
  { name: "Retargeting Q2", impressions: "67K", clicks: "5.1K", ctr: "7.6%", spend: "$1,120" },
]

export function CampaignTable() {
  return (
    <Card className="p-3 sm:p-6 bg-[#0f0f0f] border border-[#252525] rounded-xl shadow-lg">
      <h3 className="text-base sm:text-lg font-semibold text-white mb-3 sm:mb-4">Recent Campaigns</h3>
      <div className="overflow-x-auto -mx-3 sm:mx-0">
        <div className="inline-block min-w-full align-middle">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#252525]">
                <th className="text-left py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm font-medium text-gray-400 whitespace-nowrap">
                  Campaign
                </th>
                <th className="text-left py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm font-medium text-gray-400 whitespace-nowrap">
                  Impressions
                </th>
                <th className="text-left py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm font-medium text-gray-400 whitespace-nowrap">
                  Clicks
                </th>
                <th className="text-left py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm font-medium text-gray-400 whitespace-nowrap">
                  CTR
                </th>
                <th className="text-left py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm font-medium text-gray-400 whitespace-nowrap">
                  Spend
                </th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map((campaign, index) => (
                <tr key={index} className="border-b border-[#1f1f1f] hover:bg-[#141414] transition-colors">
                  <td className="py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm font-medium text-white whitespace-nowrap">
                    {campaign.name}
                  </td>
                  <td className="py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm text-gray-400 whitespace-nowrap">
                    {campaign.impressions}
                  </td>
                  <td className="py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm text-gray-400 whitespace-nowrap">
                    {campaign.clicks}
                  </td>
                  <td className="py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm text-gray-400 whitespace-nowrap">
                    {campaign.ctr}
                  </td>
                  <td className="py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm font-medium text-white whitespace-nowrap">
                    {campaign.spend}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Card>
  )
}
