"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { toast } from "sonner"
import { Instagram, Facebook, Music2, Trash2, RefreshCw } from "lucide-react"

interface SocialAccount {
  id: number
  platform: string
  username: string
  display_name: string
  profile_image_url?: string
  is_active: boolean
  connected_at: string
}

export default function SettingsPage() {
  const [accounts, setAccounts] = useState<SocialAccount[]>([])
  const [loading, setLoading] = useState(true)
  const [connecting, setConnecting] = useState<string | null>(null)

  // TODO: Get user ID from authentication
  const userId = null // Replace with auth.user?.id when auth is implemented

  useEffect(() => {
    fetchAccounts()

    // Check for OAuth callback
    const params = new URLSearchParams(window.location.search)
    const connected = params.get('connected')
    const error = params.get('error')
    const accountsParam = params.get('accounts')

    if (connected) {
      toast.success(`Successfully connected ${connected} account(s)!`)
      if (accountsParam) {
        const connectedAccounts = JSON.parse(decodeURIComponent(accountsParam))
        connectedAccounts.forEach((acc: any) => {
          toast.success(`✓ ${acc.platform}: @${acc.name}`)
        })
      }
      // Clean URL
      window.history.replaceState({}, '', '/dashboard/settings')
      fetchAccounts()
    }

    if (error) {
      toast.error(`Connection failed: ${error}`)
      window.history.replaceState({}, '', '/dashboard/settings')
    }
  }, [])

  const fetchAccounts = async () => {
    try {
      const response = await fetch(`/api/social/accounts?userId=${userId}`)
      const data = await response.json()
      setAccounts(data.accounts || [])
    } catch (error) {
      console.error('Error fetching accounts:', error)
    } finally {
      setLoading(false)
    }
  }

  const connectPlatform = (platform: string) => {
    setConnecting(platform)
    const connectUrl = platform === 'meta'
      ? `/api/social/connect/meta?userId=${userId}`
      : `/api/social/connect/tiktok?userId=${userId}`

    window.location.href = connectUrl
  }

  const disconnectAccount = async (accountId: number) => {
    if (!confirm('Are you sure you want to disconnect this account?')) {
      return
    }

    try {
      const response = await fetch(`/api/social/accounts/${accountId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        toast.success('Account disconnected')
        fetchAccounts()
      } else {
        toast.error('Failed to disconnect account')
      }
    } catch (error) {
      toast.error('Failed to disconnect account')
    }
  }

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'instagram':
        return <Instagram className="w-5 h-5" />
      case 'facebook':
        return <Facebook className="w-5 h-5" />
      case 'tiktok':
        return <Music2 className="w-5 h-5" />
      default:
        return null
    }
  }

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'instagram':
        return 'from-purple-600 to-pink-600'
      case 'facebook':
        return 'from-blue-600 to-blue-500'
      case 'tiktok':
        return 'from-black to-gray-800'
      default:
        return 'from-gray-600 to-gray-500'
    }
  }

  const hasInstagram = accounts.some(acc => acc.platform === 'instagram')
  const hasFacebook = accounts.some(acc => acc.platform === 'facebook')
  const hasTikTok = accounts.some(acc => acc.platform === 'tiktok')

  return (
    <div className="p-4 sm:p-6 xl:px-8 xl:py-6 bg-[#0a0a0a] min-h-screen">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-semibold text-white mb-2">Settings</h1>
        <p className="text-gray-400 mb-8">
          Connect your social media accounts to publish videos and track analytics
        </p>

        {/* Connect New Account */}
        <Card className="p-6 bg-[#0f0f0f] border border-[#252525] mb-6">
          <h2 className="text-lg font-semibold text-white mb-4">Connect Accounts</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Instagram */}
            <button
              onClick={() => connectPlatform('meta')}
              disabled={connecting === 'meta'}
              className={`relative overflow-hidden rounded-xl p-6 text-left transition-all hover:scale-105 ${
                hasInstagram ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${getPlatformColor('instagram')} opacity-90`} />
              <div className="relative">
                <Instagram className="w-8 h-8 text-white mb-3" />
                <h3 className="text-white font-semibold mb-1">Instagram</h3>
                <p className="text-white/80 text-sm">
                  {hasInstagram ? 'Connected' : 'Publish Reels & Stories'}
                </p>
              </div>
            </button>

            {/* Facebook */}
            <button
              onClick={() => connectPlatform('meta')}
              disabled={connecting === 'meta'}
              className={`relative overflow-hidden rounded-xl p-6 text-left transition-all hover:scale-105 ${
                hasFacebook ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${getPlatformColor('facebook')} opacity-90`} />
              <div className="relative">
                <Facebook className="w-8 h-8 text-white mb-3" />
                <h3 className="text-white font-semibold mb-1">Facebook</h3>
                <p className="text-white/80 text-sm">
                  {hasFacebook ? 'Connected' : 'Post to Pages'}
                </p>
              </div>
            </button>

            {/* TikTok */}
            <button
              onClick={() => connectPlatform('tiktok')}
              disabled={connecting === 'tiktok'}
              className={`relative overflow-hidden rounded-xl p-6 text-left transition-all hover:scale-105 ${
                hasTikTok ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${getPlatformColor('tiktok')} opacity-90`} />
              <div className="relative">
                <Music2 className="w-8 h-8 text-white mb-3" />
                <h3 className="text-white font-semibold mb-1">TikTok</h3>
                <p className="text-white/80 text-sm">
                  {hasTikTok ? 'Connected' : 'Share Videos'}
                </p>
              </div>
            </button>
          </div>

          {connecting && (
            <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
              <p className="text-blue-400 text-sm flex items-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin" />
                Redirecting to {connecting === 'meta' ? 'Meta' : 'TikTok'} for authorization...
              </p>
            </div>
          )}
        </Card>

        {/* Connected Accounts */}
        <Card className="p-6 bg-[#0f0f0f] border border-[#252525]">
          <h2 className="text-lg font-semibold text-white mb-4">Connected Accounts</h2>

          {loading ? (
            <div className="text-center py-8">
              <RefreshCw className="w-6 h-6 text-gray-400 animate-spin mx-auto mb-2" />
              <p className="text-gray-400 text-sm">Loading accounts...</p>
            </div>
          ) : accounts.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-400 mb-2">No accounts connected yet</p>
              <p className="text-gray-500 text-sm">
                Connect an account above to start publishing videos
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {accounts.map((account) => (
                <div
                  key={account.id}
                  className="flex items-center justify-between p-4 bg-[#0a0a0a] rounded-lg border border-[#252525]"
                >
                  <div className="flex items-center gap-4">
                    {/* Platform Icon */}
                    <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${getPlatformColor(account.platform)} flex items-center justify-center`}>
                      {account.profile_image_url ? (
                        <img
                          src={account.profile_image_url}
                          alt={account.username}
                          className="w-full h-full rounded-full object-cover"
                        />
                      ) : (
                        <div className="text-white">
                          {getPlatformIcon(account.platform)}
                        </div>
                      )}
                    </div>

                    {/* Account Info */}
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-white font-medium">@{account.username}</p>
                        <Badge
                          variant={account.is_active ? "default" : "secondary"}
                          className={account.is_active ? "bg-green-500/20 text-green-400" : ""}
                        >
                          {account.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </div>
                      <p className="text-gray-400 text-sm capitalize">
                        {account.platform} • Connected {new Date(account.connected_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  {/* Actions */}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => disconnectAccount(account.id)}
                    className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Disconnect
                  </Button>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Info Box */}
        <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
          <p className="text-blue-400 text-sm mb-2 font-medium">💡 Tips:</p>
          <ul className="text-blue-300/80 text-sm space-y-1 list-disc list-inside">
            <li>Instagram requires a Business or Creator account</li>
            <li>Facebook connects to Pages you manage</li>
            <li>You can connect multiple accounts per platform</li>
            <li>Accounts need periodic re-authorization (every 60 days)</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
