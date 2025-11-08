'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Plus, Search } from 'lucide-react'

export default function CampaignsPage() {
  const { user, loading } = useAuth()
  const [campaigns, setCampaigns] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!loading && user?.id) {
      fetchCampaigns()
    } else if (!loading && !user) {
      setIsLoading(false)
    }
  }, [user?.id, loading])

  const fetchCampaigns = async () => {
    if (!user?.id) return
    
    try {
      const response = await fetch(`/api/campaigns?userId=${user.id}`)
      const data = await response.json()
      
      if (data.success) {
        setCampaigns(data.campaigns)
      } else {
        setError('Failed to load campaigns')
      }
    } catch (err) {
      setError('Failed to load campaigns')
    } finally {
      setIsLoading(false)
    }
  }

  if (loading || isLoading) {
    return <div className="p-6 text-white">Loading...</div>
  }

  if (!user) {
    return (
      <div className="p-6 bg-[#0a0a0a] min-h-screen">
        <Card className="bg-[#111111] border-[#252525]">
          <CardContent className="p-8 text-center">
            <h3 className="text-lg font-medium text-white mb-2">Authentication Required</h3>
            <p className="text-gray-400">Please sign in to view campaigns</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="p-6 bg-[#0a0a0a] min-h-screen">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-white mb-4">Campaigns</h1>
        
        <div className="flex gap-3 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <Input placeholder="Search campaigns..." className="pl-10 bg-[#0a0a0a] border-[#252525] text-white" />
          </div>
          <Button className="bg-blue-600 hover:bg-blue-700">
            <Plus className="w-4 h-4 mr-2" />
            New Campaign
          </Button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-900/20 border border-red-500 rounded text-red-400">
          {error}
        </div>
      )}

      {campaigns.length === 0 ? (
        <Card className="bg-[#111111] border-[#252525]">
          <CardContent className="p-8 text-center">
            <h3 className="text-lg font-medium text-white mb-2">No campaigns yet</h3>
            <p className="text-gray-400 mb-4">Create your first campaign to get started</p>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              Create Campaign
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {campaigns.map((campaign: any) => (
            <Card key={campaign.id} className="bg-[#111111] border-[#252525]">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-white">{campaign.product_name}</CardTitle>
                    <p className="text-gray-400 text-sm">{campaign.campaign_type}</p>
                  </div>
                  <Badge variant={campaign.status === 'completed' ? 'default' : 'secondary'}>
                    {campaign.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300 text-sm">{campaign.product_description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
