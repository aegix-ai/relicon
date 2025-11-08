'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Search, Filter, Play, Download, Share2 } from 'lucide-react'

export default function AdsPage() {
  const { user, loading } = useAuth()
  const [ads, setAds] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!loading && user) {
      fetchAds()
    } else if (!loading && !user) {
      setIsLoading(false)
    }
  }, [user, loading])

  const fetchAds = async () => {
    try {
      const response = await fetch(`/api/videos?userId=${user.id}`)
      const data = await response.json()
      
      if (data.success) {
        setAds(data.videos)
      } else {
        setError('Failed to load ads')
      }
    } catch (err) {
      setError('Failed to load ads')
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
            <p className="text-gray-400">Please sign in to view your ads</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="p-4 sm:p-6 xl:px-8 xl:py-6 bg-[#0a0a0a] min-h-screen">
      <div className="mb-4 sm:mb-6">
        <h1 className="text-xl sm:text-2xl font-semibold text-white mb-3 sm:mb-4">Ads Archive</h1>

        <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <Input
              placeholder="Search ads..."
              className="pl-10 rounded-md bg-[#0a0a0a] border-[#252525] text-white placeholder:text-gray-600 h-10 sm:h-auto"
            />
          </div>
          <Button variant="outline" className="border-[#252525] text-white hover:bg-[#252525] h-10 sm:h-auto">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </Button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-900/20 border border-red-500 rounded text-red-400">
          {error}
        </div>
      )}

      {ads.length === 0 ? (
        <Card className="bg-[#111111] border-[#252525]">
          <CardContent className="p-8 text-center">
            <Play className="w-12 h-12 text-gray-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No ads created yet</h3>
            <p className="text-gray-400 mb-4">Start creating video ads in the Studio</p>
            <Button className="bg-blue-600 hover:bg-blue-700">
              Go to Studio
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
          {ads.map((ad: any) => (
            <Card key={ad.id} className="bg-[#111111] border-[#252525] overflow-hidden group hover:border-[#404040] transition-colors">
              <div className="aspect-[9/16] bg-[#1a1a1a] relative overflow-hidden">
                {ad.video_url ? (
                  <video 
                    className="w-full h-full object-cover"
                    poster={ad.thumbnail_url}
                    preload="metadata"
                  >
                    <source src={ad.video_url} type="video/mp4" />
                  </video>
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Play className="w-8 h-8 text-gray-500" />
                  </div>
                )}
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                  <Button size="sm" className="bg-white/20 hover:bg-white/30 text-white border-0">
                    <Play className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <CardContent className="p-3 sm:p-4">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-medium text-white text-sm truncate flex-1 mr-2">
                    {ad.product_name}
                  </h3>
                  <Badge variant={ad.status === 'completed' ? 'default' : 'secondary'} className="text-xs">
                    {ad.status}
                  </Badge>
                </div>
                <p className="text-xs text-gray-400 mb-3 line-clamp-2">
                  {ad.campaign_type}
                </p>
                <div className="flex items-center gap-1">
                  <Button size="sm" variant="ghost" className="h-7 px-2 text-gray-400 hover:text-white">
                    <Download className="w-3 h-3" />
                  </Button>
                  <Button size="sm" variant="ghost" className="h-7 px-2 text-gray-400 hover:text-white">
                    <Share2 className="w-3 h-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
