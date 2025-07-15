"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Link, CheckCircle, AlertCircle, Settings, TrendingUp, DollarSign, ShoppingBag } from "lucide-react"

// Only the three platforms you specified
const platforms = [
  {
    id: "shopify",
    name: "Shopify",
    logo: "/shopify-logo.png",
    type: "ecommerce",
    connected: false,
    status: "Not Connected",
    description: "Connect your Shopify store to track sales revenue and customer data for ROI analysis",
    metrics: { orders: 0, revenue: "$0", conversion: "0%" },
    color: "bg-green-600",
    oauthUrl: "https://accounts.shopify.com/oauth/authorize",
    scopes: ["read_orders", "read_customers", "read_products"]
  },
  {
    id: "meta",
    name: "Meta (Facebook & Instagram)",
    logo: "/meta-logo.png", 
    type: "advertising",
    connected: false,
    status: "Not Connected",
    description: "Connect Meta Business Manager to track Facebook and Instagram ad performance",
    metrics: { campaigns: 0, spend: "$0", roas: "0x" },
    color: "bg-blue-500",
    oauthUrl: "https://www.facebook.com/v19.0/dialog/oauth",
    scopes: ["ads_read", "ads_management", "business_management"]
  },
  {
    id: "tiktok",
    name: "TikTok",
    logo: "/tiktok-logo.png",
    type: "advertising", 
    connected: false,
    status: "Not Connected",
    description: "Connect TikTok Ads Manager to track your TikTok advertising campaigns",
    metrics: { campaigns: 0, spend: "$0", roas: "0x" },
    color: "bg-pink-500",
    oauthUrl: "https://business-api.tiktok.com/portal/auth",
    scopes: ["campaign.read", "ad.read", "reporting.read"]
  }
]

export default function ConnectAccountsPanel() {
  const [connecting, setConnecting] = useState<string | null>(null)
  const [connectedPlatforms, setConnectedPlatforms] = useState<string[]>([])

  // Listen for OAuth callback messages
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === "oauth_success") {
        const { platform, code } = event.data
        console.log(`OAuth success for ${platform}:`, code)
        
        // Add to connected platforms
        setConnectedPlatforms(prev => [...prev, platform])
        setConnecting(null)
        
        // Here you would typically send the code to your backend
        // to exchange for an access token
      } else if (event.data.type === "oauth_error") {
        const { platform, error } = event.data
        console.error(`OAuth error for ${platform}:`, error)
        setConnecting(null)
      }
    }

    window.addEventListener("message", handleMessage)
    return () => window.removeEventListener("message", handleMessage)
  }, [])

  const handleConnect = (platform: typeof platforms[0]) => {
    setConnecting(platform.id)
    
    // Generate OAuth URL with proper parameters
    const clientId = process.env.NEXT_PUBLIC_CLIENT_ID || "demo_client_id"
    const redirectUri = encodeURIComponent(`${window.location.origin}/auth/callback/${platform.id}`)
    const scopes = platform.scopes.join(',')
    
    let oauthUrl = ""
    
    switch (platform.id) {
      case "shopify":
        oauthUrl = `${platform.oauthUrl}?client_id=${clientId}&scope=${scopes}&redirect_uri=${redirectUri}&response_type=code`
        break
      case "meta":
        oauthUrl = `${platform.oauthUrl}?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scopes}&response_type=code`
        break
      case "tiktok":
        oauthUrl = `${platform.oauthUrl}?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scopes}&response_type=code`
        break
    }
    
    // Open OAuth popup
    const popup = window.open(
      oauthUrl,
      `${platform.name}_oauth`,
      'width=500,height=600,scrollbars=yes,resizable=yes'
    )
    
    // Check if popup was closed manually
    const checkClosed = setInterval(() => {
      if (popup?.closed) {
        clearInterval(checkClosed)
        setConnecting(null)
      }
    }, 1000)
  }

  const handleDisconnect = (platformId: string) => {
    setConnectedPlatforms(prev => prev.filter(id => id !== platformId))
  }

  const connectedCount = connectedPlatforms.length
  const adPlatforms = platforms.filter(p => p.type === "advertising")
  const ecommercePlatforms = platforms.filter(p => p.type === "ecommerce")

  return (
    <div className="p-6 space-y-8 bg-gray-900 dark:bg-gray-900 light:bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white dark:text-white light:text-gray-900 mb-4 flex items-center justify-center">
          <Link className="w-8 h-8 mr-3 text-[#FF5C00]" />
          Connect Your Accounts
        </h2>
        <p className="text-gray-300 dark:text-gray-300 light:text-gray-700 text-lg max-w-2xl mx-auto">
          Connect your essential platforms to enable automatic performance tracking and ROI analysis
        </p>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-gray-800 dark:bg-gray-800 light:bg-white border-gray-700 dark:border-gray-700 light:border-gray-200">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <Link className="w-6 h-6 text-[#FF5C00]" />
              <Badge variant="outline" className="border-green-500 text-green-400">
                {connectedCount}/3 Connected
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white dark:text-white light:text-gray-900">
              {connectedCount}
            </div>
            <div className="text-gray-400 dark:text-gray-400 light:text-gray-600 text-sm">
              Connected Platforms
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 dark:bg-gray-800 light:bg-white border-gray-700 dark:border-gray-700 light:border-gray-200">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <TrendingUp className="w-6 h-6 text-blue-500" />
              <Badge variant="outline" className="border-blue-500 text-blue-400">
                {adPlatforms.filter(p => connectedPlatforms.includes(p.id)).length} Active
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white dark:text-white light:text-gray-900">
              Ad Tracking
            </div>
            <div className="text-gray-400 dark:text-gray-400 light:text-gray-600 text-sm">
              Performance Analytics
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 dark:bg-gray-800 light:bg-white border-gray-700 dark:border-gray-700 light:border-gray-200">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <ShoppingBag className="w-6 h-6 text-green-500" />
              <Badge variant="outline" className="border-green-500 text-green-400">
                {ecommercePlatforms.filter(p => connectedPlatforms.includes(p.id)).length} Active
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white dark:text-white light:text-gray-900">
              Sales Tracking
            </div>
            <div className="text-gray-400 dark:text-gray-400 light:text-gray-600 text-sm">
              Revenue Analytics
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Essential Platforms */}
      <div className="space-y-6">
        <div className="flex items-center space-x-3">
          <Link className="w-6 h-6 text-[#FF5C00]" />
          <h3 className="text-2xl font-bold text-white dark:text-white light:text-gray-900">
            Essential Platforms
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {platforms.map((platform) => {
            const isConnected = connectedPlatforms.includes(platform.id)
            const isConnecting = connecting === platform.id
            
            return (
              <Card
                key={platform.id}
                className={`transition-all duration-300 hover:shadow-lg ${
                  isConnected
                    ? "bg-gray-800 dark:bg-gray-800 light:bg-white border-green-500"
                    : "bg-gray-800 dark:bg-gray-800 light:bg-white border-gray-700 dark:border-gray-700 light:border-gray-200 hover:border-[#FF5C00]"
                }`}
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`w-12 h-12 rounded-lg ${platform.color} flex items-center justify-center text-white font-bold text-xl`}>
                        {platform.name.charAt(0)}
                      </div>
                      <div>
                        <CardTitle className="text-white dark:text-white light:text-gray-900">
                          {platform.name}
                        </CardTitle>
                        <div className="flex items-center space-x-2 mt-1">
                          {isConnected ? (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          ) : (
                            <AlertCircle className="w-4 h-4 text-gray-400" />
                          )}
                          <span
                            className={`text-sm ${
                              isConnected ? "text-green-400" : "text-gray-400 dark:text-gray-400 light:text-gray-600"
                            }`}
                          >
                            {isConnected ? "Connected" : "Not Connected"}
                          </span>
                        </div>
                      </div>
                    </div>
                    {isConnected && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-gray-600 dark:border-gray-600 light:border-gray-300 text-gray-300 dark:text-gray-300 light:text-gray-700"
                        onClick={() => handleDisconnect(platform.id)}
                      >
                        <Settings className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <CardDescription className="text-gray-300 dark:text-gray-300 light:text-gray-700">
                    {platform.description}
                  </CardDescription>

                  {isConnected && platform.type === "advertising" && (
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div>
                        <div className="text-lg font-bold text-white dark:text-white light:text-gray-900">
                          {platform.metrics.campaigns}
                        </div>
                        <div className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-600">
                          Campaigns
                        </div>
                      </div>
                      <div>
                        <div className="text-lg font-bold text-white dark:text-white light:text-gray-900">
                          {platform.metrics.spend}
                        </div>
                        <div className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-600">
                          Spend
                        </div>
                      </div>
                      <div>
                        <div className="text-lg font-bold text-[#FF5C00]">
                          {platform.metrics.roas}
                        </div>
                        <div className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-600">
                          ROAS
                        </div>
                      </div>
                    </div>
                  )}

                  {isConnected && platform.type === "ecommerce" && (
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div>
                        <div className="text-lg font-bold text-white dark:text-white light:text-gray-900">
                          {platform.metrics.orders}
                        </div>
                        <div className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-600">
                          Orders
                        </div>
                      </div>
                      <div>
                        <div className="text-lg font-bold text-white dark:text-white light:text-gray-900">
                          {platform.metrics.revenue}
                        </div>
                        <div className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-600">
                          Revenue
                        </div>
                      </div>
                      <div>
                        <div className="text-lg font-bold text-[#FF5C00]">
                          {platform.metrics.conversion}
                        </div>
                        <div className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-600">
                          Conversion
                        </div>
                      </div>
                    </div>
                  )}

                  <Button
                    onClick={() => isConnected ? handleDisconnect(platform.id) : handleConnect(platform)}
                    disabled={isConnecting}
                    className={`w-full transition-all duration-300 ${
                      isConnected
                        ? "bg-red-600 hover:bg-red-700 text-white"
                        : "bg-[#FF5C00] hover:bg-[#E05000] text-white"
                    }`}
                  >
                    {isConnecting ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                        Connecting...
                      </>
                    ) : isConnected ? (
                      "Disconnect"
                    ) : (
                      "Connect Account"
                    )}
                  </Button>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Connection Status */}
      {connectedCount > 0 && (
        <Card className="bg-gray-800 dark:bg-gray-800 light:bg-white border-gray-700 dark:border-gray-700 light:border-gray-200">
          <CardHeader>
            <CardTitle className="text-white dark:text-white light:text-gray-900 flex items-center">
              <CheckCircle className="w-5 h-5 mr-2 text-green-500" />
              Integration Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-300 dark:text-gray-300 light:text-gray-700">
                  Automatic data collection
                </span>
                <Badge variant="outline" className="border-green-500 text-green-400">
                  Active
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300 dark:text-gray-300 light:text-gray-700">
                  Performance tracking
                </span>
                <Badge variant="outline" className="border-green-500 text-green-400">
                  Running
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300 dark:text-gray-300 light:text-gray-700">
                  ROI analysis
                </span>
                <Badge variant="outline" className="border-green-500 text-green-400">
                  Enabled
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Next Steps */}
      {connectedCount < 3 && (
        <Card className="bg-gray-800 dark:bg-gray-800 light:bg-white border-gray-700 dark:border-gray-700 light:border-gray-200">
          <CardHeader>
            <CardTitle className="text-white dark:text-white light:text-gray-900 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2 text-[#FF5C00]" />
              Next Steps
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <p className="text-gray-300 dark:text-gray-300 light:text-gray-700">
                Connect all platforms to unlock the full power of Relicon AI:
              </p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center text-gray-300 dark:text-gray-300 light:text-gray-700">
                  <div className="w-2 h-2 bg-[#FF5C00] rounded-full mr-3"></div>
                  Automatic performance tracking and optimization
                </li>
                <li className="flex items-center text-gray-300 dark:text-gray-300 light:text-gray-700">
                  <div className="w-2 h-2 bg-[#FF5C00] rounded-full mr-3"></div>
                  Real-time ROI analysis and reporting  
                </li>
                <li className="flex items-center text-gray-300 dark:text-gray-300 light:text-gray-700">
                  <div className="w-2 h-2 bg-[#FF5C00] rounded-full mr-3"></div>
                  AI-powered campaign optimization suggestions
                </li>
              </ul>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}