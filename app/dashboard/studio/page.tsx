"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Loader2, Heart, MessageCircle, Share2, Bookmark, Play, Pause } from "lucide-react"
import Image from "next/image"
import { toast } from "sonner"

interface FormData {
  productName: string
  productDescription: string
  campaignType: string
  targetAudience: string
  creativeStyle: string
}

interface JobStatus {
  status: string
  progress?: number
  message?: string
  video_url?: string
  current_step?: string
}

export default function StudioPage() {
  const [isGenerating, setIsGenerating] = useState(false)
  const [jobId, setJobId] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState("")
  const [videoUrl, setVideoUrl] = useState<string | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [videoElement, setVideoElement] = useState<HTMLVideoElement | null>(null)

  const [formData, setFormData] = useState<FormData>({
    productName: "",
    productDescription: "",
    campaignType: "",
    targetAudience: "",
    creativeStyle: ""
  })

  const handleCreate = async () => {
    if (!formData.productName || !formData.productDescription) {
      toast.error("Please fill in product name and description")
      return
    }

    setIsGenerating(true)
    setProgress(0)
    setCurrentStep("Initializing...")

    try {
      const response = await fetch("/api/engine/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          brand_name: "Relicon",
          brand_description: "AI-powered advertising platform",
          product_name: formData.productName,
          product_description: formData.productDescription,
          target_audience: formData.targetAudience || "general audience",
          tone: "professional",
          duration: 18,
          call_to_action: "Learn more",
          creative_style: formData.creativeStyle || "modern"
        })
      })

      if (!response.ok) {
        throw new Error("Failed to start generation")
      }

      const data = await response.json()
      setJobId(data.job_id)
      toast.success("Ad generation started!")
    } catch (error) {
      console.error("Generation error:", error)
      toast.error("Failed to start ad generation")
      setIsGenerating(false)
    }
  }

  useEffect(() => {
    if (!jobId || !isGenerating) return

    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/engine/status/${jobId}`)
        const status: JobStatus = await response.json()

        if (status.progress) {
          setProgress(status.progress)
        }

        if (status.current_step) {
          setCurrentStep(status.current_step)
        } else if (status.message) {
          setCurrentStep(status.message)
        }

        if (status.status === "completed" && status.video_url) {
          setVideoUrl(status.video_url)
          setIsGenerating(false)
          setProgress(100)
          toast.success("Ad generated successfully!")
          clearInterval(pollInterval)
        } else if (status.status === "failed") {
          setIsGenerating(false)
          toast.error(status.message || "Generation failed")
          clearInterval(pollInterval)
        }
      } catch (error) {
        console.error("Status check error:", error)
      }
    }, 2000)

    return () => clearInterval(pollInterval)
  }, [jobId, isGenerating])

  const togglePlayPause = () => {
    if (!videoElement) return

    if (isPlaying) {
      videoElement.pause()
    } else {
      videoElement.play()
    }
    setIsPlaying(!isPlaying)
  }

  return (
    <div className="p-4 sm:p-6 xl:px-8 xl:py-6 bg-[#0a0a0a] min-h-screen">
      <h1 className="text-xl sm:text-2xl font-semibold text-white mb-4 sm:mb-6">Creative Studio</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {/* Left Panel - Form Inputs */}
        <Card className="p-4 sm:p-6 bg-[#0f0f0f] border border-[#252525] rounded-xl shadow-lg">
          <h2 className="text-base sm:text-lg font-semibold text-white mb-4 sm:mb-6">Campaign Setup</h2>

          <div className="space-y-4 sm:space-y-5">
            {/* Product Name */}
            <div className="space-y-2">
              <Label htmlFor="product-name" className="text-sm font-medium text-gray-300">
                Product Name
              </Label>
              <Input
                id="product-name"
                type="text"
                placeholder="Enter product name..."
                value={formData.productName}
                onChange={(e) => setFormData({ ...formData, productName: e.target.value })}
                className="rounded-md bg-[#0a0a0a] border-[#252525] text-white placeholder:text-gray-600"
              />
            </div>

            {/* Product Description */}
            <div className="space-y-2">
              <Label htmlFor="description" className="text-sm font-medium text-gray-300">
                Product Description
              </Label>
              <Textarea
                id="description"
                placeholder="Describe your product or service..."
                value={formData.productDescription}
                onChange={(e) => setFormData({ ...formData, productDescription: e.target.value })}
                className="rounded-md min-h-24 resize-none bg-[#0a0a0a] border-[#252525] text-white placeholder:text-gray-600"
              />
            </div>

            {/* Campaign Type */}
            <div className="space-y-2">
              <Label htmlFor="campaign-type" className="text-sm font-medium text-gray-300">
                Campaign Type
              </Label>
              <Select value={formData.campaignType} onValueChange={(value) => setFormData({ ...formData, campaignType: value })}>
                <SelectTrigger id="campaign-type" className="rounded-md bg-[#0a0a0a] border-[#252525] text-white">
                  <SelectValue placeholder="Select campaign type" />
                </SelectTrigger>
                <SelectContent className="bg-[#0f0f0f] border-[#252525] text-white">
                  <SelectItem value="awareness">Brand Awareness</SelectItem>
                  <SelectItem value="conversion">Conversion</SelectItem>
                  <SelectItem value="engagement">Engagement</SelectItem>
                  <SelectItem value="traffic">Traffic</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Audience */}
            <div className="space-y-2">
              <Label htmlFor="audience" className="text-sm font-medium text-gray-300">
                Target Audience
              </Label>
              <Textarea
                id="audience"
                placeholder="Describe your target audience..."
                value={formData.targetAudience}
                onChange={(e) => setFormData({ ...formData, targetAudience: e.target.value })}
                className="rounded-md min-h-20 resize-none bg-[#0a0a0a] border-[#252525] text-white placeholder:text-gray-600"
              />
            </div>

            {/* Tuning Options */}
            <div className="space-y-2">
              <Label htmlFor="tuning" className="text-sm font-medium text-gray-300">
                Creative Tuning
              </Label>
              <Select value={formData.creativeStyle} onValueChange={(value) => setFormData({ ...formData, creativeStyle: value })}>
                <SelectTrigger id="tuning" className="rounded-md bg-[#0a0a0a] border-[#252525] text-white">
                  <SelectValue placeholder="Select creative style" />
                </SelectTrigger>
                <SelectContent className="bg-[#0f0f0f] border-[#252525] text-white">
                  <SelectItem value="bold">Bold & Energetic</SelectItem>
                  <SelectItem value="minimal">Minimal & Clean</SelectItem>
                  <SelectItem value="luxury">Luxury & Premium</SelectItem>
                  <SelectItem value="playful">Playful & Fun</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button
              onClick={handleCreate}
              disabled={isGenerating}
              className="w-full bg-white hover:bg-gray-200 text-black rounded-md h-11 font-medium disabled:opacity-50"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                "Create Ad"
              )}
            </Button>
          </div>
        </Card>

        {/* Right Panel - TikTok Preview */}
        <div className="relative">
          <div className="relative w-full bg-black overflow-hidden h-full min-h-[500px] sm:min-h-[640px]">
            {/* Left Gradient Border */}
            <div className="absolute left-0 top-0 bottom-0 w-6 sm:w-12 bg-gradient-to-r from-black to-transparent z-10" />

            {/* Right Gradient Border */}
            <div className="absolute right-0 top-0 bottom-0 w-6 sm:w-12 bg-gradient-to-l from-black to-transparent z-10" />

            {/* 9:16 TikTok Frame - Centered */}
            <div className="absolute inset-0 flex items-start justify-center pt-0">
              <div className="w-full max-w-[280px] sm:max-w-[360px] h-full">
                <div className="w-full h-full bg-black overflow-hidden relative shadow-2xl">
                  {isGenerating ? (
                    <div className="absolute inset-0 flex items-center justify-center bg-[#0a0a0a]">
                      <div className="text-center">
                        <Loader2 className="w-12 h-12 mx-auto mb-3 text-white animate-spin" />
                        <p className="text-sm text-gray-400 mb-2">{currentStep || "Creating your ad..."}</p>
                        <div className="mt-4 w-48 mx-auto bg-[#161616] rounded-full h-2 overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-gray-400 to-white transition-all duration-500" 
                            style={{ width: `${progress}%` }}
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-2">{progress}%</p>
                      </div>
                    </div>
                  ) : (
                    <>
                      {/* Top Bar */}
                      <div className="absolute top-0 left-0 right-0 z-20 bg-gradient-to-b from-black/60 to-transparent pt-3 pb-8 px-4">
                        <div className="flex items-center justify-center gap-6 text-white text-sm font-medium">
                          <span className="text-gray-300">Following</span>
                          <span className="relative">
                            For You
                            <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-8 h-0.5 bg-white rounded-full" />
                          </span>
                        </div>
                      </div>

                      {/* Main Content - Video or Placeholder */}
                      <div className="absolute inset-0" onClick={togglePlayPause}>
                        {videoUrl ? (
                          <video
                            ref={setVideoElement}
                            src={videoUrl}
                            className="w-full h-full object-cover"
                            loop
                            playsInline
                          />
                        ) : (
                          <Image
                            src="/modern-product-advertisement-vertical-format.jpg"
                            alt="Ad Content"
                            fill
                            className="object-cover"
                          />
                        )}
                        
                        {videoUrl && (
                          <div className="absolute inset-0 flex items-center justify-center">
                            <div className={`bg-black/50 rounded-full p-4 transition-opacity ${isPlaying ? 'opacity-0' : 'opacity-100'}`}>
                              {isPlaying ? (
                                <Pause className="w-12 h-12 text-white" />
                              ) : (
                                <Play className="w-12 h-12 text-white" />
                              )}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Right Side Actions */}
                      <div className="absolute right-3 bottom-24 z-20 flex flex-col items-center gap-5">
                        <div className="flex flex-col items-center">
                          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-pink-500 via-red-500 to-yellow-500 p-[2.5px] mb-1 shadow-lg">
                            <div className="w-full h-full rounded-full bg-white overflow-hidden">
                              <Image
                                src="/professional-business-person.png"
                                alt="Brand"
                                width={48}
                                height={48}
                                className="object-cover w-full h-full"
                              />
                            </div>
                          </div>
                        </div>
                        <div className="flex flex-col items-center gap-1">
                          <Heart className="w-8 h-8 text-white drop-shadow-lg" />
                          <span className="text-white text-xs font-semibold drop-shadow-lg">25.3k</span>
                        </div>
                        <div className="flex flex-col items-center gap-1">
                          <MessageCircle className="w-8 h-8 text-white drop-shadow-lg" />
                          <span className="text-white text-xs font-semibold drop-shadow-lg">3456</span>
                        </div>
                        <div className="flex flex-col items-center gap-1">
                          <Bookmark className="w-8 h-8 text-white drop-shadow-lg" />
                          <span className="text-white text-xs font-semibold drop-shadow-lg">1256</span>
                        </div>
                        <div className="flex flex-col items-center gap-1">
                          <Share2 className="w-8 h-8 text-white drop-shadow-lg" />
                        </div>
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-pink-500 to-purple-500 flex items-center justify-center">
                          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="white">
                            <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z" />
                          </svg>
                        </div>
                      </div>

                      {/* Bottom Info */}
                      <div className="absolute bottom-0 left-0 right-0 z-20 bg-gradient-to-t from-black/80 via-black/40 to-transparent p-4 pb-20">
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <span className="text-white font-semibold text-sm">@{formData.productName || "YourBrand"}</span>
                            <span className="text-xs text-gray-300 bg-white/20 px-2 py-0.5 rounded">Sponsored</span>
                          </div>
                          <p className="text-white text-sm leading-relaxed">
                            {formData.productDescription || "Check out our amazing product! Limited time offer 🔥"}
                          </p>
                          <div className="flex items-center gap-2 text-white text-xs">
                            <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z" />
                            </svg>
                            <span>Original Sound - Relicon AI</span>
                          </div>
                          <button className="w-full bg-white text-black font-semibold py-2.5 rounded-lg text-sm mt-2">
                            Learn More
                          </button>
                        </div>
                      </div>

                      {/* Bottom Navigation */}
                      <div className="absolute bottom-0 left-0 right-0 z-30 bg-black h-16 flex items-center justify-around px-4">
                        <div className="flex flex-col items-center gap-1">
                          <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" />
                          </svg>
                          <span className="text-white text-xs">Home</span>
                        </div>
                        <div className="flex flex-col items-center gap-1">
                          <svg className="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" />
                          </svg>
                          <span className="text-gray-400 text-xs">Discover</span>
                        </div>
                        <div className="relative -mt-4">
                          <div className="w-12 h-9 bg-gradient-to-r from-cyan-400 via-pink-500 to-purple-500 rounded-lg flex items-center justify-center">
                            <svg className="w-6 h-6 text-black font-bold" fill="currentColor" viewBox="0 0 24 24">
                              <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
                            </svg>
                          </div>
                        </div>
                        <div className="flex flex-col items-center gap-1">
                          <div className="relative">
                            <svg className="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                              <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14l4 4V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z" />
                            </svg>
                            <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center text-white text-[10px] font-bold">
                              9
                            </div>
                          </div>
                          <span className="text-gray-400 text-xs">Inbox</span>
                        </div>
                        <div className="flex flex-col items-center gap-1">
                          <svg className="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                          </svg>
                          <span className="text-gray-400 text-xs">Me</span>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>

            <div className="hidden sm:flex absolute right-2 sm:right-4 top-1/2 -translate-y-1/2 flex-col gap-2 sm:gap-3 z-20">
              <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-full px-3 sm:px-4 py-1.5 sm:py-2 shadow-xl">
                <p className="text-[9px] sm:text-[10px] text-gray-300 mb-0.5 text-center">Format</p>
                <p className="text-[10px] sm:text-xs font-medium text-white text-center whitespace-nowrap">9:16</p>
              </div>
              <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-full px-3 sm:px-4 py-1.5 sm:py-2 shadow-xl">
                <p className="text-[9px] sm:text-[10px] text-gray-300 mb-0.5 text-center">Duration</p>
                <p className="text-[10px] sm:text-xs font-medium text-white text-center whitespace-nowrap">18s</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
