"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Link, CheckCircle, AlertCircle, Settings, Zap, TrendingUp, Users, DollarSign, ShoppingBag } from "lucide-react"

const adPlatforms = [
  {
    name: "TikTok",
    logo: "/tiktok-logo.png",
    connected: true,
    status: "Active",
    description: "Connect your TikTok Ads Manager for automated campaign management",
    metrics: { campaigns: 12, spend: "$2,840", roas: "4.2x" },
    color: "bg-pink-500",
  },
  {
    name: "Meta (Facebook & Instagram)",
    logo: "/meta-logo.png",
    connected: true,
    status: "Active",
    description: "Sync with Meta Business Manager for Facebook and Instagram ads",
    metrics: { campaigns: 8, spend: "$3,200", roas: "3.8x" },
    color: "bg-blue-500",
  },
  {
    name: "YouTube",
    logo: "/youtube-logo.png",
    connected: false,
    status: "Not Connected",
    description: "Connect YouTube Ads for video advertising campaigns",
    metrics: { campaigns: 0, spend: "$0", roas: "0x" },
    color: "bg-red-500",
  },
  {
    name: "Google Ads",
    logo: "/google-logo.png",
    connected: false,
    status: "Not Connected",
    description: "Integrate Google Ads for search and display campaigns",
    metrics: { campaigns: 0, spend: "$0", roas: "0x" },
    color: "bg-green-500",
  },
  {
    name: "Snapchat",
    logo: "/snapchat-logo.png",
    connected: false,
    status: "Not Connected",
    description: "Connect Snapchat Ads Manager for Gen Z targeting",
    metrics: { campaigns: 0, spend: "$0", roas: "0x" },
    color: "bg-yellow-500",
  },
  {
    name: "Pinterest",
    logo: "/pinterest-logo.png",
    connected: false,
    status: "Not Connected",
    description: "Integrate Pinterest Business for visual discovery ads",
    metrics: { campaigns: 0, spend: "$0", roas: "0x" },
    color: "bg-purple-500",
  },
]

const salesPlatforms = [
  {
    name: "Shopify",
    logo: "/shopify-logo.png",
    connected: true,
    status: "Active",
    description: "Sync your Shopify store for revenue tracking and customer data",
    metrics: { orders: 1240, revenue: "$32,040", conversion: "3.2%" },
    color: "bg-green-600",
  },
  {
    name: "Stripe",
    logo: "/stripe-logo.png",
    connected: true,
    status: "Active",
    description: "Connect Stripe for payment processing and revenue analytics",
    metrics: { transactions: 2180, revenue: "$28,560", fees: "$856" },
    color: "bg-purple-600",
  },
  {
    name: "WooCommerce",
    logo: "/woocommerce-logo.png",
    connected: false,
    status: "Not Connected",
    description: "Integrate WooCommerce for WordPress e-commerce tracking",
    metrics: { orders: 0, revenue: "$0", conversion: "0%" },
    color: "bg-blue-600",
  },
  {
    name: "BigCommerce",
    logo: "/bigcommerce-logo.png",
    connected: false,
    status: "Not Connected",
    description: "Connect BigCommerce for comprehensive sales analytics",
    metrics: { orders: 0, revenue: "$0", conversion: "0%" },
    color: "bg-orange-600",
  },
  {
    name: "Square",
    logo: "/square-logo.png",
    connected: false,
    status: "Not Connected",
    description: "Integrate Square for in-person and online sales tracking",
    metrics: { transactions: 0, revenue: "$0", fees: "$0" },
    color: "bg-gray-600",
  },
  {
    name: "PayPal",
    logo: "/paypal-logo.png",
    connected: false,
    status: "Not Connected",
    description: "Connect PayPal for payment processing and customer insights",
    metrics: { transactions: 0, revenue: "$0", fees: "$0" },
    color: "bg-blue-700",
  },
]

export default function ConnectAccountsPanel() {
  const [connecting, setConnecting] = useState<string | null>(null)

  const handleConnect = (platformName: string) => {
    setConnecting(platformName)
    setTimeout(() => {
      setConnecting(null)
      // Here you would handle the actual connection logic
    }, 2000)
  }

  const connectedAdPlatforms = adPlatforms.filter((p) => p.connected).length
  const connectedSalesPlatforms = salesPlatforms.filter((p) => p.connected).length
  const totalAdSpend = adPlatforms.reduce(
    (sum, p) => sum + Number.parseFloat(p.metrics.spend.replace("$", "").replace(",", "")),
    0,
  )
  const totalRevenue = salesPlatforms.reduce(
    (sum, p) => sum + Number.parseFloat(p.metrics.revenue.replace("$", "").replace(",", "")),
    0,
  )

  return (
    <div className="p-6 space-y-8 bg-gray-900 dark:bg-gray-900 light:bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white dark:text-white light:text-gray-900 mb-4 flex items-center justify-center">
          <Link className="w-8 h-8 mr-3 text-[#FF5C00]" />
          Connect Your Accounts
        </h2>
        <p className="text-gray-300 dark:text-gray-300 light:text-gray-700 text-lg">
          Integrate your advertising and sales platforms to unlock the full power of ReelForge AI
        </p>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <Link className="w-6 h-6 text-[#FF5C00]" />
            <Badge variant="outline" className="border-green-500 text-green-400">
              {connectedAdPlatforms} Connected
            </Badge>
          </div>
          <div className="text-2xl font-bold text-white dark:text-white light:text-gray-900">
            {connectedAdPlatforms}/6
          </div>
          <div className="text-gray-400 dark:text-gray-400 light:text-gray-600 text-sm">Ad Platforms</div>
        </div>

        <div className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <ShoppingBag className="w-6 h-6 text-blue-500" />
            <Badge variant="outline" className="border-blue-500 text-blue-400">
              {connectedSalesPlatforms} Connected
            </Badge>
          </div>
          <div className="text-2xl font-bold text-white dark:text-white light:text-gray-900">
            {connectedSalesPlatforms}/6
          </div>
          <div className="text-gray-400 dark:text-gray-400 light:text-gray-600 text-sm">Sales Platforms</div>
        </div>

        <div className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="w-6 h-6 text-red-500" />
            <TrendingUp className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-2xl font-bold text-white dark:text-white light:text-gray-900">
            ${totalAdSpend.toLocaleString()}
          </div>
          <div className="text-gray-400 dark:text-gray-400 light:text-gray-600 text-sm">Total Ad Spend</div>
        </div>

        <div className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-6 h-6 text-green-500" />
            <TrendingUp className="w-4 h-4 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-white dark:text-white light:text-gray-900">
            ${totalRevenue.toLocaleString()}
          </div>
          <div className="text-gray-400 dark:text-gray-400 light:text-gray-600 text-sm">Total Revenue</div>
        </div>
      </div>

      {/* Ad Platforms Section */}
      <div className="space-y-6">
        <div className="flex items-center space-x-3">
          <Link className="w-6 h-6 text-[#FF5C00]" />
          <h3 className="text-2xl font-bold text-white dark:text-white light:text-gray-900">Advertising Platforms</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {adPlatforms.map((platform) => (
            <div
              key={platform.name}
              className={`bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border transition-all duration-300 shadow-lg ${
                platform.connected
                  ? "border-green-500"
                  : "border-gray-700 dark:border-gray-700 light:border-gray-200 hover:border-[#FF5C00]"
              }`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <img
                    src={platform.logo || "/placeholder.svg"}
                    alt={`${platform.name} logo`}
                    className="w-10 h-10 rounded-lg"
                  />
                  <div>
                    <h3 className="text-lg font-semibold text-white dark:text-white light:text-gray-900">
                      {platform.name}
                    </h3>
                    <div className="flex items-center space-x-2">
                      {platform.connected ? (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-gray-400" />
                      )}
                      <span
                        className={`text-sm ${platform.connected ? "text-green-400" : "text-gray-400 dark:text-gray-400 light:text-gray-600"}`}
                      >
                        {platform.status}
                      </span>
                    </div>
                  </div>
                </div>
                {platform.connected && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="border-gray-600 dark:border-gray-600 light:border-gray-300 text-gray-300 dark:text-gray-300 light:text-gray-700"
                  >
                    <Settings className="w-4 h-4" />
                  </Button>
                )}
              </div>

              <p className="text-gray-300 dark:text-gray-300 light:text-gray-700 text-sm mb-4">
                {platform.description}
              </p>

              {platform.connected && (
                <div className="grid grid-cols-3 gap-2 mb-4 text-center">
                  <div>
                    <div className="text-lg font-bold text-white dark:text-white light:text-gray-900">
                      {platform.metrics.campaigns}
                    </div>
                    <div className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-600">Campaigns</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-white dark:text-white light:text-gray-900">
                      {platform.metrics.spend}
                    </div>
                    <div className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-600">Spend</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-[#FF5C00]">{platform.metrics.roas}</div>
                    <div className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-600">ROAS</div>
                  </div>
                </div>
              )}

              <Button
                onClick={() => handleConnect(platform.name)}
                disabled={connecting === platform.name}
                className={`w-full transition-all duration-300 ${
                  platform.connected
                    ? "bg-green-600 hover:bg-green-700 text-white"
                    : "bg-[#FF5C00] hover:bg-[#E05000] text-white"
                }`}
              >
                {connecting === platform.name ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Connecting...
                  </>
                ) : platform.connected ? (
                  "Connected ✓"
                ) : (
                  "Connect Account"
                )}
              </Button>
            </div>
          ))}
        </div>
      </div>

      {/* Sales Platforms Section */}
      <div className="space-y-6">
        <div className="flex items-center space-x-3">
          <ShoppingBag className="w-6 h-6 text-[#FF5C00]" />
          <h3 className="text-2xl font-bold text-white dark:text-white light:text-gray-900">
            Sales & E-commerce Platforms
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {salesPlatforms.map((platform) => (
            <div
              key={platform.name}
              className={`bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border transition-all duration-300 shadow-lg ${
                platform.connected
                  ? "border-green-500"
                  : "border-gray-700 dark:border-gray-700 light:border-gray-200 hover:border-[#FF5C00]"
              }`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <img
                    src={platform.logo || "/placeholder.svg"}
                    alt={`${platform.name} logo`}
                    className="w-10 h-10 rounded-lg"
                  />
                  <div>
                    <h3 className="text-lg font-semibold text-white dark:text-white light:text-gray-900">
                      {platform.name}
                    </h3>
                    <div className="flex items-center space-x-2">
                      {platform.connected ? (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-gray-400" />
                      )}
                      <span
                        className={`text-sm ${platform.connected ? "text-green-400" : "text-gray-400 dark:text-gray-400 light:text-gray-600"}`}
                      >
                        {platform.status}
                      </span>
                    </div>
                  </div>
                </div>
                {platform.connected && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="border-gray-600 dark:border-gray-600 light:border-gray-300 text-gray-300 dark:text-gray-300 light:text-gray-700"
                  >
                    <Settings className="w-4 h-4" />
                  </Button>
                )}
              </div>

              <p className="text-gray-300 dark:text-gray-300 light:text-gray-700 text-sm mb-4">
                {platform.description}
              </p>

              {platform.connected && (
                <div className="grid grid-cols-3 gap-2 mb-4 text-center">
                  <div>
                    <div className="text-lg font-bold text-white dark:text-white light:text-gray-900">
                      {platform.metrics.orders || platform.metrics.transactions}
                    </div>
                    <div className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-600">
                      {platform.metrics.orders ? "Orders" : "Transactions"}
                    </div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-white dark:text-white light:text-gray-900">
                      {platform.metrics.revenue}
                    </div>
                    <div className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-600">Revenue</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-[#FF5C00]">
                      {platform.metrics.conversion || platform.metrics.fees}
                    </div>
                    <div className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-600">
                      {platform.metrics.conversion ? "Conversion" : "Fees"}
                    </div>
                  </div>
                </div>
              )}

              <Button
                onClick={() => handleConnect(platform.name)}
                disabled={connecting === platform.name}
                className={`w-full transition-all duration-300 ${
                  platform.connected
                    ? "bg-green-600 hover:bg-green-700 text-white"
                    : "bg-[#FF5C00] hover:bg-[#E05000] text-white"
                }`}
              >
                {connecting === platform.name ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Connecting...
                  </>
                ) : platform.connected ? (
                  "Connected ✓"
                ) : (
                  "Connect Account"
                )}
              </Button>
            </div>
          ))}
        </div>
      </div>

      {/* Benefits Section */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-700 dark:from-gray-800 dark:to-gray-700 light:from-gray-100 light:to-gray-200 rounded-xl p-8 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
        <h3 className="text-2xl font-bold text-white dark:text-white light:text-gray-900 mb-6 text-center">
          Why Connect Your Accounts?
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="w-16 h-16 bg-[#FF5C00] rounded-full flex items-center justify-center mx-auto mb-4">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <h4 className="text-lg font-semibold text-white dark:text-white light:text-gray-900 mb-2">
              Automated Optimization
            </h4>
            <p className="text-gray-300 dark:text-gray-300 light:text-gray-700 text-sm">
              Our AI automatically optimizes your campaigns across all platforms for maximum ROAS
            </p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-[#FF5C00] rounded-full flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="w-8 h-8 text-white" />
            </div>
            <h4 className="text-lg font-semibold text-white dark:text-white light:text-gray-900 mb-2">
              Complete Revenue Attribution
            </h4>
            <p className="text-gray-300 dark:text-gray-300 light:text-gray-700 text-sm">
              Track the complete customer journey from ad click to purchase across all platforms
            </p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-[#FF5C00] rounded-full flex items-center justify-center mx-auto mb-4">
              <Users className="w-8 h-8 text-white" />
            </div>
            <h4 className="text-lg font-semibold text-white dark:text-white light:text-gray-900 mb-2">
              Unified Customer Data
            </h4>
            <p className="text-gray-300 dark:text-gray-300 light:text-gray-700 text-sm">
              Sync customer data across advertising and sales platforms for better targeting
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
