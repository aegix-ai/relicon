"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Loader2, Heart, MessageCircle, Share2, Bookmark, Play, Pause, Send, Download } from "lucide-react"
import Image from "next/image"
import { toast } from "sonner"
import { PublishModal } from "@/components/PublishModal"

interface FormData {
  productName: string
  productDescription: string
  campaignType: string
  targetAudience: string
  creativeStyle: string
  productImage: File | null
}

interface JobStatus {
  status: string
  progress?: number
  message?: string
  video_url?: string
  current_step?: string
  video_id?: number
}

export default function StudioPage() {
  const [isGenerating, setIsGenerating] = useState(false)
  const [jobId, setJobId] = useState<string | null>(null)
  const [videoId, setVideoId] = useState<number | null>(null)
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState("")
  const [videoUrl, setVideoUrl] = useState<string | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [videoElement, setVideoElement] = useState<HTMLVideoElement | null>(null)
  const [publishModalOpen, setPublishModalOpen] = useState(false)
  const [imagePreview, setImagePreview] = useState<string | null>(null)

  const [formData, setFormData] = useState<FormData>({
    productName: "",
    productDescription: "",
    campaignType: "",
    targetAudience: "",
    creativeStyle: "",
    productImage: null
  })

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (!file.type.startsWith('image/')) {
        toast.error("Please upload an image file")
        return
      }

      if (file.size > 5 * 1024 * 1024) {
        toast.error("Image size must be less than 5MB")
        return
      }

      setFormData({ ...formData, productImage: file })

      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleCreate = async () => {
    if (!formData.productName || !formData.productDescription) {
      toast.error("Please fill in product name and description")
      return
    }

    setIsGenerating(true)
    setProgress(0)
    setCurrentStep("Initializing...")

    try {
      let productImageUrl: string | undefined = undefined

      if (formData.productImage) {
        setCurrentStep("Uploading product image...")

        const uploadFormData = new FormData()
        uploadFormData.append('file', formData.productImage)
        uploadFormData.append('productName', formData.productName)

        const uploadResponse = await fetch("/api/upload-product-image", {
          method: "POST",
          body: uploadFormData
        })

        if (!uploadResponse.ok) {
          throw new Error("Failed to upload product image")
        }

        const uploadData = await uploadResponse.json()
        productImageUrl = uploadData.url
        toast.success("Product image uploaded!")
      }

      setCurrentStep("Starting video generation...")

      const response = await fetch("/api/engine/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          brand_name: formData.productName,
          brand_description: formData.productDescription,
          product_name: formData.productName,
          product_description: formData.productDescription,
          target_audience: formData.targetAudience || "general audience",
          tone: "professional",
          duration: 18,
          call_to_action: "Learn more",
          creative_style: formData.creativeStyle || "modern",
          product_image_url: productImageUrl
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
      setIsGenerating(false)
      toast.error("Failed to start generation")
    }
  }

  // Fixed polling with better state management
  useEffect(() => {
    if (!jobId || !isGenerating) return

    let pollInterval: NodeJS.Timeout

    const pollStatus = async () => {
      try {
        const response = await fetch(`/api/engine/status/${jobId}`, {
          cache: 'no-store', // Prevent caching
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        })
        
        if (!response.ok) {
          throw new Error(`Status check failed: ${response.status}`)
        }

        const status: JobStatus = await response.json()
        console.log('Status update:', status)

        // Force state updates
        setProgress(prev => {
          const newProgress = status.progress || 0
          if (newProgress !== prev) {
            console.log(`Progress: ${prev} -> ${newProgress}`)
          }
          return newProgress
        })

        setCurrentStep(prev => {
          const newStep = status.current_step || status.message || ""
          if (newStep !== prev) {
            console.log(`Step: ${prev} -> ${newStep}`)
          }
          return newStep
        })

        if (status.status === "completed" && status.video_url) {
          setVideoUrl(status.video_url)
          setVideoId(status.video_id || null)
          setIsGenerating(false)
          setProgress(100)
          toast.success("Ad generated successfully!")
          clearInterval(pollInterval)
        } else if (status.status === "failed") {
          setIsGenerating(false)
          setProgress(0)
          toast.error(status.message || "Generation failed")
          clearInterval(pollInterval)
        }
      } catch (error) {
        console.error("Status check error:", error)
        // Don't stop polling on single error
      }
    }

    // Initial check
    pollStatus()
    
    // Poll every 1.5 seconds for more responsive updates
    pollInterval = setInterval(pollStatus, 1500)

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval)
      }
    }
  }, [jobId, isGenerating])

  const togglePlay = () => {
    if (videoElement) {
      if (isPlaying) {
        videoElement.pause()
      } else {
        videoElement.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  const downloadVideo = () => {
    if (videoUrl) {
      const link = document.createElement('a')
      link.href = videoUrl
      link.download = `${formData.productName.toLowerCase().replace(/\s+/g, '-')}-ad-${Date.now()}.mp4`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Creative Studio</h1>
        <p className="text-muted-foreground">Create professional video ads with AI in minutes</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column - Form */}
        <div className="space-y-6">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Product Information</h2>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="productName">Product Name *</Label>
                <Input
                  id="productName"
                  value={formData.productName}
                  onChange={(e) => setFormData({ ...formData, productName: e.target.value })}
                  placeholder="Enter your product name"
                />
              </div>

              <div>
                <Label htmlFor="productDescription">Product Description *</Label>
                <Textarea
                  id="productDescription"
                  value={formData.productDescription}
                  onChange={(e) => setFormData({ ...formData, productDescription: e.target.value })}
                  placeholder="Describe your product's key features and benefits"
                  rows={4}
                />
              </div>

              <div>
                <Label htmlFor="targetAudience">Target Audience</Label>
                <Input
                  id="targetAudience"
                  value={formData.targetAudience}
                  onChange={(e) => setFormData({ ...formData, targetAudience: e.target.value })}
                  placeholder="e.g., Young professionals, fitness enthusiasts"
                />
              </div>

              <div>
                <Label htmlFor="creativeStyle">Creative Style</Label>
                <Select value={formData.creativeStyle} onValueChange={(value) => setFormData({ ...formData, creativeStyle: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a style" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="modern">Modern & Clean</SelectItem>
                    <SelectItem value="energetic">Energetic & Dynamic</SelectItem>
                    <SelectItem value="professional">Professional & Corporate</SelectItem>
                    <SelectItem value="playful">Playful & Fun</SelectItem>
                    <SelectItem value="luxury">Luxury & Premium</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Product Image Upload */}
              <div>
                <Label>Product Image (Optional)</Label>
                <div className="mt-2">
                  {imagePreview ? (
                    <div className="relative">
                      <img
                        src={imagePreview}
                        alt="Product preview"
                        className="w-full h-32 object-cover rounded-lg border"
                      />
                      <button
                        onClick={() => {
                          setFormData({ ...formData, productImage: null })
                          setImagePreview(null)
                        }}
                        className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm hover:bg-red-600"
                      >
                        ×
                      </button>
                    </div>
                  ) : (
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleImageChange}
                        className="hidden"
                        id="product-image"
                      />
                      <label
                        htmlFor="product-image"
                        className="cursor-pointer text-sm text-gray-600 hover:text-gray-800"
                      >
                        Click to upload product image
                        <br />
                        <span className="text-xs text-gray-400">PNG, JPG, WebP up to 5MB</span>
                      </label>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <Button 
              onClick={handleCreate} 
              disabled={isGenerating || !formData.productName || !formData.productDescription}
              className="w-full mt-6"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating Ad...
                </>
              ) : (
                "Create Ad"
              )}
            </Button>
          </Card>
        </div>

        {/* Right Column - Preview */}
        <div className="space-y-6">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Preview</h2>
            
            <div className="aspect-[9/16] bg-black rounded-lg overflow-hidden relative max-w-[300px] mx-auto">
              {videoUrl ? (
                <>
                  <video
                    ref={setVideoElement}
                    src={videoUrl}
                    className="w-full h-full object-cover"
                    onPlay={() => setIsPlaying(true)}
                    onPause={() => setIsPlaying(false)}
                    controls={false}
                  />
                  
                  {/* Video Controls */}
                  <div className="absolute bottom-4 left-4 right-4 flex justify-between items-center">
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={togglePlay}
                      className="bg-black/50 hover:bg-black/70 text-white"
                    >
                      {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                    </Button>
                    
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={downloadVideo}
                        className="bg-black/50 hover:bg-black/70 text-white"
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                      
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => setPublishModalOpen(true)}
                        className="bg-black/50 hover:bg-black/70 text-white"
                      >
                        <Send className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </>
              ) : isGenerating ? (
                <div className="flex flex-col items-center justify-center h-full text-white">
                  <Loader2 className="h-8 w-8 animate-spin mb-4" />
                  <div className="text-center px-4">
                    <div className="text-sm font-medium mb-2">
                      {progress}% Complete
                    </div>
                    <div className="text-xs text-gray-300 mb-4">
                      {currentStep}
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-400">
                  <div className="text-center">
                    <div className="text-lg mb-2">📱</div>
                    <div className="text-sm">Your ad will appear here</div>
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>

      {/* Publish Modal */}
      <PublishModal
        isOpen={publishModalOpen}
        onClose={() => setPublishModalOpen(false)}
        videoUrl={videoUrl}
        videoId={videoId}
      />
    </div>
  )
}
