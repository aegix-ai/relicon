"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Badge } from "@/components/ui/badge"
import { Upload, Play, Loader2, Sparkles, Brain, Target, Palette } from "lucide-react"

const platforms = ["TikTok", "Meta", "YouTube", "Instagram"]
const tones = ["Friendly", "Luxury", "Bold", "Calm", "Professional", "Playful"]
const visualStyles = ["UGC", "Motion", "Clean", "Hype", "Minimal", "Cinematic"]
const voiceoverOptions = ["AI Generated", "Human Voice", "No Voiceover"]

const adPreviews = ["/ad-preview-1.png", "/ad-preview-2.png", "/ad-preview-3.png"]

export default function AICreationPanel() {
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([])
  const [adDuration, setAdDuration] = useState([15])
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationStep, setGenerationStep] = useState(0)
  const [currentPreview, setCurrentPreview] = useState(0)

  const togglePlatform = (platform: string) => {
    setSelectedPlatforms((prev) => (prev.includes(platform) ? prev.filter((p) => p !== platform) : [...prev, platform]))
  }

  const [formData, setFormData] = useState({
    brandName: '',
    brandDescription: '',
    targetAudience: '',
    tone: '',
    duration: 30,
    callToAction: ''
  })
  const [videoUrl, setVideoUrl] = useState<string | null>(null)
  const [jobId, setJobId] = useState<string | null>(null)

  const handleGenerateAd = async () => {
    if (!formData.brandName || !formData.brandDescription) {
      alert('Please fill in at least Brand Name and Brand Description');
      return;
    }

    setIsGenerating(true)
    setGenerationStep(0)
    setVideoUrl(null)

    try {
      // Call our backend API
      const response = await fetch('http://localhost:5000/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          brand_name: formData.brandName,
          brand_description: formData.brandDescription,
          target_audience: formData.targetAudience || 'general audience',
          tone: formData.tone || 'professional',
          duration: formData.duration,
          call_to_action: formData.callToAction || 'Take action now'
        }),
      })

      const result = await response.json()
      
      if (result.job_id) {
        setJobId(result.job_id)
        pollJobStatus(result.job_id)
      } else {
        throw new Error('Failed to start video generation')
      }
    } catch (error) {
      console.error('Error generating video:', error)
      setIsGenerating(false)
      alert('Failed to start video generation. Please try again.')
    }
  }

  const pollJobStatus = async (jobId: string) => {
    const poll = async () => {
      try {
        const response = await fetch(`http://localhost:5000/api/status/${jobId}`)
        const status = await response.json()
        
        // Update generation step based on progress
        if (status.progress <= 20) {
          setGenerationStep(1) // Analyzing brand
        } else if (status.progress <= 40) {
          setGenerationStep(2) // Generating script
        } else if (status.progress <= 60) {
          setGenerationStep(3) // Creating audio
        } else if (status.progress <= 80) {
          setGenerationStep(4) // Creating visuals
        } else if (status.progress < 100) {
          setGenerationStep(5) // Finalizing
        }

        if (status.status === 'completed' && status.video_url) {
          setIsGenerating(false)
          setVideoUrl(status.video_url)
          setGenerationStep(6)
        } else if (status.status === 'failed') {
          setIsGenerating(false)
          alert(`Video generation failed: ${status.message}`)
        } else if (status.status === 'processing') {
          setTimeout(poll, 2000) // Poll every 2 seconds
        }
      } catch (error) {
        console.error('Error polling job status:', error)
        setTimeout(poll, 5000) // Retry after 5 seconds
      }
    }
    
    setTimeout(poll, 1000) // Start polling after 1 second
  }

  const generationSteps = [
    "Analyzing brand tone and audience",
    "Generating AI script with natural pacing",
    "Creating voiceover with ElevenLabs AI",
    "Generating dynamic scenes and transitions",
    "Assembling final video with synchronized captions",
    "✓ Video ready!"
  ]

  return (
    <div className="p-6 space-y-8 bg-gray-900 dark:bg-gray-900 light:bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white dark:text-white light:text-gray-900 mb-4 flex items-center justify-center">
          <Brain className="w-8 h-8 mr-3 text-[#FF5C00]" />
          Ad Engine Studio
        </h2>
        <p className="text-gray-300 dark:text-gray-300 light:text-gray-700 text-lg">
          Let our AI agents create high-converting ads tailored to your brand and audience
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Input Form */}
        <div className="lg:col-span-2 space-y-8">
          {/* Brand & Product Section */}
          <div className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
            <h3 className="text-xl font-semibold text-white dark:text-white light:text-gray-900 mb-6 flex items-center">
              <Target className="w-5 h-5 mr-2 text-[#FF5C00]" />
              Brand & Product Details
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 dark:text-gray-300 light:text-gray-700 mb-2">
                  Brand Name *
                </label>
                <Input
                  placeholder="Enter your brand name"
                  value={formData.brandName}
                  onChange={(e) => setFormData(prev => ({...prev, brandName: e.target.value}))}
                  className="bg-gray-700 dark:bg-gray-700 light:bg-gray-100 border-gray-600 dark:border-gray-600 light:border-gray-300 text-white dark:text-white light:text-gray-900 placeholder-gray-400 dark:placeholder-gray-400 light:placeholder-gray-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 dark:text-gray-300 light:text-gray-700 mb-2">
                  Brand Tone
                </label>
                <Select value={formData.tone} onValueChange={(value) => setFormData(prev => ({...prev, tone: value}))}>
                  <SelectTrigger className="bg-gray-700 dark:bg-gray-700 light:bg-gray-100 border-gray-600 dark:border-gray-600 light:border-gray-300 text-white dark:text-white light:text-gray-900">
                    <SelectValue placeholder="Select tone" />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-700 dark:bg-gray-700 light:bg-white border-gray-600 dark:border-gray-600 light:border-gray-300">
                    {tones.map((tone) => (
                      <SelectItem
                        key={tone}
                        value={tone.toLowerCase()}
                        className="text-white dark:text-white light:text-gray-900 hover:bg-gray-600 dark:hover:bg-gray-600 light:hover:bg-gray-100"
                      >
                        {tone}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-300 dark:text-gray-300 light:text-gray-700 mb-2">
                Brand Description *
              </label>
              <Textarea
                placeholder="Describe your brand/product in detail - benefits, unique selling points, what makes it special..."
                value={formData.brandDescription}
                onChange={(e) => setFormData(prev => ({...prev, brandDescription: e.target.value}))}
                className="bg-gray-700 dark:bg-gray-700 light:bg-gray-100 border-gray-600 dark:border-gray-600 light:border-gray-300 text-white dark:text-white light:text-gray-900 placeholder-gray-400 dark:placeholder-gray-400 light:placeholder-gray-500 min-h-[100px]"
              />
            </div>
          </div>

          {/* Targeting Section */}
          <div className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
            <h3 className="text-xl font-semibold text-white dark:text-white light:text-gray-900 mb-6 flex items-center">
              <Brain className="w-5 h-5 mr-2 text-[#FF5C00]" />
              AI Targeting & Platforms
            </h3>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 dark:text-gray-300 light:text-gray-700 mb-2">
                  Target Platforms
                </label>
                <div className="flex flex-wrap gap-2">
                  {platforms.map((platform) => (
                    <Badge
                      key={platform}
                      variant={selectedPlatforms.includes(platform) ? "default" : "outline"}
                      className={`cursor-pointer transition-all duration-200 ${
                        selectedPlatforms.includes(platform)
                          ? "bg-[#FF5C00] hover:bg-[#E05000] text-white"
                          : "border-gray-600 dark:border-gray-600 light:border-gray-300 text-gray-300 dark:text-gray-300 light:text-gray-700 hover:border-[#FF5C00]"
                      }`}
                      onClick={() => togglePlatform(platform)}
                    >
                      {platform}
                    </Badge>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 dark:text-gray-300 light:text-gray-700 mb-2">
                  Target Audience Description
                </label>
                <Textarea
                  placeholder="Describe your ideal customer (age, interests, behaviors, pain points)..."
                  value={formData.targetAudience}
                  onChange={(e) => setFormData(prev => ({...prev, targetAudience: e.target.value}))}
                  className="bg-gray-700 dark:bg-gray-700 light:bg-gray-100 border-gray-600 dark:border-gray-600 light:border-gray-300 text-white dark:text-white light:text-gray-900 placeholder-gray-400 dark:placeholder-gray-400 light:placeholder-gray-500 min-h-[100px]"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 dark:text-gray-300 light:text-gray-700 mb-2">
                  Call to Action
                </label>
                <Input
                  placeholder="e.g., Buy now, Sign up today, Get started..."
                  value={formData.callToAction}
                  onChange={(e) => setFormData(prev => ({...prev, callToAction: e.target.value}))}
                  className="bg-gray-700 dark:bg-gray-700 light:bg-gray-100 border-gray-600 dark:border-gray-600 light:border-gray-300 text-white dark:text-white light:text-gray-900 placeholder-gray-400 dark:placeholder-gray-400 light:placeholder-gray-500"
                />
              </div>
            </div>
          </div>

          {/* Creative Settings */}
          <div className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
            <h3 className="text-xl font-semibold text-white dark:text-white light:text-gray-900 mb-6 flex items-center">
              <Palette className="w-5 h-5 mr-2 text-[#FF5C00]" />
              Creative Settings
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 dark:text-gray-300 light:text-gray-700 mb-2">
                  Visual Style
                </label>
                <Select>
                  <SelectTrigger className="bg-gray-700 dark:bg-gray-700 light:bg-gray-100 border-gray-600 dark:border-gray-600 light:border-gray-300 text-white dark:text-white light:text-gray-900">
                    <SelectValue placeholder="Select style" />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-700 dark:bg-gray-700 light:bg-white border-gray-600 dark:border-gray-600 light:border-gray-300">
                    {visualStyles.map((style) => (
                      <SelectItem
                        key={style}
                        value={style.toLowerCase()}
                        className="text-white dark:text-white light:text-gray-900 hover:bg-gray-600 dark:hover:bg-gray-600 light:hover:bg-gray-100"
                      >
                        {style}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 dark:text-gray-300 light:text-gray-700 mb-2">
                  Voiceover
                </label>
                <Select>
                  <SelectTrigger className="bg-gray-700 dark:bg-gray-700 light:bg-gray-100 border-gray-600 dark:border-gray-600 light:border-gray-300 text-white dark:text-white light:text-gray-900">
                    <SelectValue placeholder="Select voiceover" />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-700 dark:bg-gray-700 light:bg-white border-gray-600 dark:border-gray-600 light:border-gray-300">
                    {voiceoverOptions.map((option) => (
                      <SelectItem
                        key={option}
                        value={option.toLowerCase()}
                        className="text-white dark:text-white light:text-gray-900 hover:bg-gray-600 dark:hover:bg-gray-600 light:hover:bg-gray-100"
                      >
                        {option}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-300 dark:text-gray-300 light:text-gray-700 mb-2">
                Video Duration: {formData.duration} seconds
              </label>
              <Slider 
                value={[formData.duration]} 
                onValueChange={(value) => setFormData(prev => ({...prev, duration: value[0]}))} 
                max={60} 
                min={15} 
                step={15} 
                className="w-full" 
              />
              <div className="flex justify-between text-sm text-gray-400 mt-1">
                <span>15s</span>
                <span>30s</span>
                <span>45s</span>
                <span>60s</span>
              </div>
            </div>
          </div>

          {/* Media Upload */}
          <div className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
            <h3 className="text-xl font-semibold text-white dark:text-white light:text-gray-900 mb-6 flex items-center">
              <Upload className="w-5 h-5 mr-2 text-[#FF5C00]" />
              Product Media
            </h3>
            <div className="border-2 border-dashed border-gray-600 dark:border-gray-600 light:border-gray-300 rounded-lg p-8 text-center hover:border-[#FF5C00] transition-colors duration-200">
              <Upload className="w-12 h-12 text-gray-400 dark:text-gray-400 light:text-gray-500 mx-auto mb-4" />
              <p className="text-gray-400 dark:text-gray-400 light:text-gray-600 mb-2">
                Drag & drop your product images or videos
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-500 light:text-gray-500">
                Supports JPG, PNG, MP4 up to 50MB
              </p>
              <Button
                variant="outline"
                className="mt-4 border-gray-600 dark:border-gray-600 light:border-gray-300 text-gray-300 dark:text-gray-300 light:text-gray-700 hover:bg-gray-700 dark:hover:bg-gray-700 light:hover:bg-gray-100"
              >
                Browse Files
              </Button>
            </div>
          </div>
        </div>

        {/* Preview & Generation */}
        <div className="space-y-6">
          <div className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
            <h3 className="text-lg font-semibold text-white dark:text-white light:text-gray-900 mb-4 flex items-center">
              <Play className="w-5 h-5 mr-2 text-[#FF5C00]" />
              AI Preview
            </h3>
            {/* Vertical aspect ratio for mobile ads - smaller size */}
            <div className="aspect-[9/20] bg-gray-700 dark:bg-gray-700 light:bg-gray-200 rounded-lg flex items-center justify-center border border-gray-600 dark:border-gray-600 light:border-gray-300 mb-6 relative overflow-hidden">
              {isGenerating ? (
                <div className="text-center">
                  <Loader2 className="w-12 h-12 text-[#FF5C00] animate-spin mx-auto mb-4" />
                  <p className="text-gray-300 dark:text-gray-300 light:text-gray-700">Creating your ad...</p>
                </div>
              ) : (
                <>
                  <img
                    src={adPreviews[currentPreview] || "/placeholder.svg"}
                    alt="AI Generated Ad Preview"
                    className="w-full h-full object-cover rounded-lg"
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity duration-300">
                    <Play className="w-16 h-16 text-white drop-shadow-lg" />
                  </div>
                </>
              )}
            </div>

            <Button
              onClick={handleGenerateAd}
              disabled={isGenerating}
              className="w-full bg-[#FF5C00] hover:bg-[#E05000] text-white py-4 text-lg font-semibold rounded-lg transition-all duration-300 hover:shadow-lg disabled:opacity-50 mb-4"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5 mr-2" />
                  Generate Ad with AI
                </>
              )}
            </Button>

            <Button
              variant="outline"
              className="w-full border-[#FF5C00] text-[#FF5C00] hover:bg-[#FF5C00] hover:text-white py-4 text-lg font-semibold rounded-lg transition-all duration-300"
            >
              <Upload className="w-5 h-5 mr-2" />
              Publish to Platforms
            </Button>

            {isGenerating && (
              <div className="mt-6 bg-gray-700 dark:bg-gray-700 light:bg-gray-100 rounded-lg p-4">
                <h4 className="text-white dark:text-white light:text-gray-900 font-medium mb-4">
                  AI Generation Progress
                </h4>
                <div className="space-y-3">
                  {generationSteps.map((step, index) => (
                    <div key={index} className="flex items-center space-x-3">
                      <div
                        className={`w-3 h-3 rounded-full ${
                          index < generationStep
                            ? "bg-green-500"
                            : index === generationStep
                              ? "bg-[#FF5C00] animate-pulse"
                              : "bg-gray-500"
                        }`}
                      ></div>
                      <span
                        className={`text-sm ${
                          index < generationStep
                            ? "text-green-400"
                            : index === generationStep
                              ? "text-[#FF5C00]"
                              : "text-gray-400 dark:text-gray-400 light:text-gray-600"
                        }`}
                      >
                        {step}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {videoUrl && (
              <div className="mt-6 bg-gray-700 dark:bg-gray-700 light:bg-gray-100 rounded-lg p-4">
                <h4 className="text-white dark:text-white light:text-gray-900 font-medium mb-4">
                  🎉 Your Video is Ready!
                </h4>
                <div className="bg-black rounded-lg overflow-hidden">
                  <video 
                    controls 
                    className="w-full max-w-md mx-auto"
                    style={{ aspectRatio: '9/16' }}
                  >
                    <source src={videoUrl} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                </div>
                <div className="flex gap-3 mt-4">
                  <Button 
                    onClick={() => window.open(videoUrl, '_blank')} 
                    className="bg-[#FF5C00] hover:bg-[#E05000]"
                  >
                    Download Video
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setVideoUrl(null);
                      setGenerationStep(0);
                    }}
                    className="border-gray-600 text-gray-300 hover:bg-gray-600"
                  >
                    Create Another
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* AI Suggestions */}
          <div className="bg-gray-800 dark:bg-gray-800 light:bg-white rounded-xl p-6 border border-gray-700 dark:border-gray-700 light:border-gray-200 shadow-lg">
            <h3 className="text-lg font-semibold text-white dark:text-white light:text-gray-900 mb-4 flex items-center">
              <Brain className="w-5 h-5 mr-2 text-[#FF5C00]" />
              AI Suggestions
            </h3>
            <div className="space-y-3">
              <div className="bg-gray-700 dark:bg-gray-700 light:bg-gray-100 rounded-lg p-3">
                <p className="text-sm text-gray-300 dark:text-gray-300 light:text-gray-700">
                  <span className="text-[#FF5C00] font-medium">Hook Optimization:</span> Try starting with a question to
                  increase engagement by 34%
                </p>
              </div>
              <div className="bg-gray-700 dark:bg-gray-700 light:bg-gray-100 rounded-lg p-3">
                <p className="text-sm text-gray-300 dark:text-gray-300 light:text-gray-700">
                  <span className="text-[#FF5C00] font-medium">Platform Tip:</span> TikTok performs best with 15-second
                  vertical videos
                </p>
              </div>
              <div className="bg-gray-700 dark:bg-gray-700 light:bg-gray-100 rounded-lg p-3">
                <p className="text-sm text-gray-300 dark:text-gray-300 light:text-gray-700">
                  <span className="text-[#FF5C00] font-medium">Audience Insight:</span> Your target demographic responds
                  well to UGC-style content
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
