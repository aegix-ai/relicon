import { Card } from "@/components/ui/card"

interface Campaign {
  id: number
  name: string
  status: string
  total_budget: number
  daily_budget: number
  created_at: string
}

interface CampaignTableProps {
  campaigns: Campaign[]
}

export function CampaignTable({ campaigns }: CampaignTableProps) {
  if (!campaigns || campaigns.length === 0) {
    return (
      <Card className="p-3 sm:p-6 bg-[#0f0f0f] border border-[#252525] rounded-xl shadow-lg">
        <h3 className="text-base sm:text-lg font-semibold text-white mb-3 sm:mb-4">Recent Campaigns</h3>
        <div className="text-center py-8">
          <p className="text-gray-400">No campaigns found. Create your first campaign to get started!</p>
        </div>
      </Card>
    )
  }

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
                  Status
                </th>
                <th className="text-left py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm font-medium text-gray-400 whitespace-nowrap">
                  Total Budget
                </th>
                <th className="text-left py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm font-medium text-gray-400 whitespace-nowrap">
                  Daily Budget
                </th>
                <th className="text-left py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm font-medium text-gray-400 whitespace-nowrap">
                  Created
                </th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map((campaign) => (
                <tr key={campaign.id} className="border-b border-[#1f1f1f] hover:bg-[#141414] transition-colors">
                  <td className="py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm font-medium text-white whitespace-nowrap">
                    {campaign.name}
                  </td>
                  <td className="py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      campaign.status === 'active' 
                        ? 'bg-green-900 text-green-300' 
                        : campaign.status === 'paused'
                        ? 'bg-yellow-900 text-yellow-300'
                        : 'bg-gray-900 text-gray-300'
                    }`}>
                      {campaign.status}
                    </span>
                  </td>
                  <td className="py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm text-gray-400 whitespace-nowrap">
                    ${campaign.total_budget?.toLocaleString() || '0'}
                  </td>
                  <td className="py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm text-gray-400 whitespace-nowrap">
                    ${campaign.daily_budget?.toLocaleString() || '0'}
                  </td>
                  <td className="py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm font-medium text-white whitespace-nowrap">
                    {new Date(campaign.created_at).toLocaleDateString()}
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
