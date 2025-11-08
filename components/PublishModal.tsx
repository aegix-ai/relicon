"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Instagram, Facebook, Music2, Loader2, ExternalLink, Calendar } from "lucide-react"
import { toast } from "sonner"

interface SocialAccount {
  id: number
  platform: string
  username: string
  display_name: string
  profile_image_url?: string
}

interface PublishModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  videoId: number
  videoUrl: string
  productName: string
  productDescription: string
}

export function PublishModal({
  open,
  onOpenChange,
  videoId,
  videoUrl,
  productName,
  productDescription
}: PublishModalProps) {
  const [accounts, setAccounts] = useState<SocialAccount[]>([])
  const [selectedAccountId, setSelectedAccountId] = useState<number | null>(null)
  const [caption, setCaption] = useState("")
  const [hashtags, setHashtags] = useState("")
  const [scheduledFor, setScheduledFor] = useState("")
  const [loading, setLoading] = useState(false)
  const [publishing, setPublishing] = useState(false)

  // TODO: Get user ID from authentication
  const userId = null // Replace with auth.user?.id when auth is implemented

  useEffect(() => {
    if (open) {
      fetchAccounts()
      // Pre-fill caption
      setCaption(productDescription || `Check out ${productName}! 🚀`)
    }
  }, [open, productDescription, productName])

  const fetchAccounts = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/social/accounts?userId=${userId}`)
      const data = await response.json()
      setAccounts(data.accounts || [])

      if (data.accounts?.length === 0) {
        toast.error('No social accounts connected', {
          description: 'Please connect an account in Settings first',
          action: {
            label: 'Go to Settings',
            onClick: () => window.location.href = '/dashboard/settings'
          }
        })
      }
    } catch (error) {
      console.error('Error fetching accounts:', error)
      toast.error('Failed to load social accounts')
    } finally {
      setLoading(false)
    }
  }

  const handlePublish = async () => {
    if (!selectedAccountId) {
      toast.error('Please select an account')
      return
    }

    setPublishing(true)

    try {
      const hashtagArray = hashtags
        .split(',')
        .map(tag => tag.trim().replace('#', ''))
        .filter(tag => tag.length > 0)

      const response = await fetch('/api/social/publish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          videoId: videoId,
          socialAccountId: selectedAccountId,
          caption: caption,
          hashtags: hashtagArray,
          scheduledFor: scheduledFor || null
        })
      })

      const data = await response.json()

      if (data.success) {
        const selectedAccount = accounts.find(acc => acc.id === selectedAccountId)

        if (scheduledFor) {
          toast.success('Post scheduled!', {
            description: `Will be published to ${selectedAccount?.platform} on ${new Date(scheduledFor).toLocaleString()}`
          })
        } else {
          toast.success('Published successfully!', {
            description: `Your video is now live on ${selectedAccount?.platform}`,
            action: data.permalink ? {
              label: 'View Post',
              onClick: () => window.open(data.permalink, '_blank')
            } : undefined
          })
        }

        onOpenChange(false)

        // Reset form
        setSelectedAccountId(null)
        setCaption("")
        setHashtags("")
        setScheduledFor("")
      } else {
        throw new Error(data.error || 'Publishing failed')
      }
    } catch (error: any) {
      console.error('Publishing error:', error)
      toast.error('Failed to publish', {
        description: error.message || 'Please try again or contact support'
      })
    } finally {
      setPublishing(false)
    }
  }

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'instagram':
        return <Instagram className="w-4 h-4" />
      case 'facebook':
        return <Facebook className="w-4 h-4" />
      case 'tiktok':
        return <Music2 className="w-4 h-4" />
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

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] bg-[#0f0f0f] border-[#252525] text-white">
        <DialogHeader>
          <DialogTitle className="text-xl">Publish to Social Media</DialogTitle>
          <DialogDescription className="text-gray-400">
            Share your AI-generated video to your connected social accounts
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {/* Video Preview */}
          <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
            <video
              src={videoUrl}
              className="w-full h-full object-contain"
              controls
              loop
            />
          </div>

          {/* Account Selection */}
          <div className="space-y-2">
            <Label>Select Account</Label>
            {loading ? (
              <div className="p-4 text-center text-gray-400">
                <Loader2 className="w-5 h-5 animate-spin mx-auto mb-2" />
                Loading accounts...
              </div>
            ) : accounts.length === 0 ? (
              <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                <p className="text-yellow-400 text-sm mb-2">No accounts connected</p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => window.location.href = '/dashboard/settings'}
                  className="text-yellow-400 border-yellow-500/30 hover:bg-yellow-500/10"
                >
                  Connect Account
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-2">
                {accounts.map((account) => (
                  <button
                    key={account.id}
                    onClick={() => setSelectedAccountId(account.id)}
                    className={`flex items-center gap-3 p-3 rounded-lg border transition-all ${
                      selectedAccountId === account.id
                        ? 'border-white bg-white/5'
                        : 'border-[#252525] hover:border-[#404040] bg-[#0a0a0a]'
                    }`}
                  >
                    <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${getPlatformColor(account.platform)} flex items-center justify-center text-white`}>
                      {account.profile_image_url ? (
                        <img
                          src={account.profile_image_url}
                          alt={account.username}
                          className="w-full h-full rounded-full object-cover"
                        />
                      ) : (
                        getPlatformIcon(account.platform)
                      )}
                    </div>
                    <div className="text-left flex-1">
                      <p className="text-white font-medium text-sm">@{account.username}</p>
                      <p className="text-gray-400 text-xs capitalize">{account.platform}</p>
                    </div>
                    {selectedAccountId === account.id && (
                      <div className="w-5 h-5 rounded-full bg-white flex items-center justify-center">
                        <svg className="w-3 h-3 text-black" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Caption */}
          <div className="space-y-2">
            <Label htmlFor="caption">Caption</Label>
            <Textarea
              id="caption"
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              placeholder="Write a caption for your video..."
              className="min-h-[100px] bg-[#0a0a0a] border-[#252525] text-white resize-none"
              maxLength={2200}
            />
            <p className="text-xs text-gray-400 text-right">
              {caption.length}/2200 characters
            </p>
          </div>

          {/* Hashtags */}
          <div className="space-y-2">
            <Label htmlFor="hashtags">Hashtags</Label>
            <Input
              id="hashtags"
              value={hashtags}
              onChange={(e) => setHashtags(e.target.value)}
              placeholder="innovation, tech, startup (comma separated)"
              className="bg-[#0a0a0a] border-[#252525] text-white"
            />
            <p className="text-xs text-gray-400">
              Enter hashtags separated by commas (without # symbol)
            </p>
          </div>

          {/* Schedule */}
          <div className="space-y-2">
            <Label htmlFor="schedule" className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Schedule (Optional)
            </Label>
            <Input
              id="schedule"
              type="datetime-local"
              value={scheduledFor}
              onChange={(e) => setScheduledFor(e.target.value)}
              min={new Date().toISOString().slice(0, 16)}
              className="bg-[#0a0a0a] border-[#252525] text-white"
            />
            <p className="text-xs text-gray-400">
              Leave empty to publish immediately
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={publishing}
              className="flex-1 border-[#252525] text-white hover:bg-[#252525]"
            >
              Cancel
            </Button>
            <Button
              onClick={handlePublish}
              disabled={publishing || !selectedAccountId || accounts.length === 0}
              className="flex-1 bg-white text-black hover:bg-gray-200"
            >
              {publishing ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Publishing...
                </>
              ) : scheduledFor ? (
                'Schedule Post'
              ) : (
                'Publish Now'
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
