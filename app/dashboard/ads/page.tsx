"use client"

import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, Filter, ArrowUpDown } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import Image from "next/image"

const adsData = [
  {
    name: "Summer Sale Hero",
    campaignType: "Conversion",
    roas: "4.2x",
    ctr: "6.8%",
    status: "active",
    thumbnail: "/summer-sale-tiktok-ad.jpg",
  },
  {
    name: "Product Launch Video",
    campaignType: "Awareness",
    roas: "3.8x",
    ctr: "5.2%",
    status: "active",
    thumbnail: "/product-launch-tiktok-ad.jpg",
  },
  {
    name: "Retargeting Banner",
    campaignType: "Conversion",
    roas: "5.1x",
    ctr: "7.3%",
    status: "active",
    thumbnail: "/retargeting-tiktok-ad.jpg",
  },
  {
    name: "Brand Story",
    campaignType: "Engagement",
    roas: "2.9x",
    ctr: "4.1%",
    status: "paused",
    thumbnail: "/brand-story-tiktok-ad.jpg",
  },
  {
    name: "Holiday Special",
    campaignType: "Conversion",
    roas: "4.7x",
    ctr: "6.5%",
    status: "completed",
    thumbnail: "/holiday-special-tiktok-ad.jpg",
  },
  {
    name: "New Collection Teaser",
    campaignType: "Traffic",
    roas: "3.2x",
    ctr: "5.8%",
    status: "active",
    thumbnail: "/collection-teaser-tiktok-ad.jpg",
  },
  {
    name: "Flash Sale Alert",
    campaignType: "Conversion",
    roas: "6.3x",
    ctr: "8.9%",
    status: "completed",
    thumbnail: "/flash-sale-tiktok-ad.jpg",
  },
  {
    name: "Customer Testimonial",
    campaignType: "Awareness",
    roas: "2.4x",
    ctr: "3.7%",
    status: "active",
    thumbnail: "/testimonial-tiktok-ad.jpg",
  },
]

export default function AdsPage() {
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
          <Button
            variant="outline"
            className="rounded-md gap-2 bg-[#0a0a0a] border-[#252525] text-gray-300 hover:bg-[#141414] hover:text-white h-10 sm:h-auto"
          >
            <Filter className="w-4 h-4" />
            <span className="hidden sm:inline">Filter</span>
          </Button>
        </div>
      </div>

      <Card className="bg-[#0f0f0f] border border-[#252525] rounded-xl shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[#0a0a0a] border-b border-[#252525]">
              <tr>
                <th className="text-left py-2 sm:py-3 px-3 sm:px-6 text-xs sm:text-sm font-medium text-gray-300">
                  Thumbnail
                </th>
                <th className="text-left py-2 sm:py-3 px-3 sm:px-6 text-xs sm:text-sm font-medium text-gray-300">
                  <button className="flex items-center gap-1 hover:text-white whitespace-nowrap">
                    Ad Name
                    <ArrowUpDown className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                  </button>
                </th>
                <th className="text-left py-2 sm:py-3 px-3 sm:px-6 text-xs sm:text-sm font-medium text-gray-300">
                  <button className="flex items-center gap-1 hover:text-white whitespace-nowrap">
                    Campaign
                    <ArrowUpDown className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                  </button>
                </th>
                <th className="text-left py-2 sm:py-3 px-3 sm:px-6 text-xs sm:text-sm font-medium text-gray-300">
                  <button className="flex items-center gap-1 hover:text-white">
                    ROAS
                    <ArrowUpDown className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                  </button>
                </th>
                <th className="text-left py-2 sm:py-3 px-3 sm:px-6 text-xs sm:text-sm font-medium text-gray-300">
                  <button className="flex items-center gap-1 hover:text-white">
                    CTR
                    <ArrowUpDown className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                  </button>
                </th>
                <th className="text-left py-2 sm:py-3 px-3 sm:px-6 text-xs sm:text-sm font-medium text-gray-300">
                  <button className="flex items-center gap-1 hover:text-white">
                    Status
                    <ArrowUpDown className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                  </button>
                </th>
              </tr>
            </thead>
            <tbody>
              {adsData.map((ad, index) => (
                <tr key={index} className="border-b border-[#1f1f1f] hover:bg-[#141414] transition-colors">
                  <td className="py-3 sm:py-4 px-3 sm:px-6">
                    <div className="relative w-12 h-12 sm:w-16 sm:h-16 rounded-lg overflow-hidden bg-[#0a0a0a] border border-[#252525]">
                      <Image src={ad.thumbnail || "/placeholder.svg"} alt={ad.name} fill className="object-cover" />
                    </div>
                  </td>
                  <td className="py-3 sm:py-4 px-3 sm:px-6 text-xs sm:text-sm font-medium text-white whitespace-nowrap">
                    {ad.name}
                  </td>
                  <td className="py-3 sm:py-4 px-3 sm:px-6 text-xs sm:text-sm text-gray-400 whitespace-nowrap">
                    {ad.campaignType}
                  </td>
                  <td className="py-3 sm:py-4 px-3 sm:px-6 text-xs sm:text-sm font-medium text-white">{ad.roas}</td>
                  <td className="py-3 sm:py-4 px-3 sm:px-6 text-xs sm:text-sm text-gray-400">{ad.ctr}</td>
                  <td className="py-3 sm:py-4 px-3 sm:px-6">
                    <Badge
                      variant={ad.status === "active" ? "default" : "secondary"}
                      className={
                        ad.status === "active"
                          ? "bg-green-500/20 text-green-400 hover:bg-green-500/20 border-green-500/30 text-xs"
                          : ad.status === "paused"
                            ? "bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/20 border-yellow-500/30 text-xs"
                            : "bg-gray-500/20 text-gray-400 hover:bg-gray-500/20 border-gray-500/30 text-xs"
                      }
                    >
                      {ad.status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
