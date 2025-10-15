import React, { useState } from 'react'

interface VideoFormProps {
  onJobCreated: (jobId: string) => void
  disabled?: boolean
}

interface FormData {
  brand_name: string
  brand_description: string
  target_audience: string
  tone: string
  duration: number
  call_to_action: string
}

export function VideoForm({ onJobCreated, disabled = false }: VideoFormProps) {
  const [formData, setFormData] = useState<FormData>({
    brand_name: '',
    brand_description: '',
    target_audience: 'general audience',
    tone: 'friendly',
    duration: 30,
    call_to_action: 'Take action now'
  })
  
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.brand_name || !formData.brand_description) {
      setError('Brand name and description are required')
      return
    }
    
    setIsSubmitting(true)
    setError(null)
    
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      onJobCreated(result.job_id)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed')
    } finally {
      setIsSubmitting(false)
    }
  }
  
  const handleChange = (field: keyof FormData, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Brand Name */}
        <div>
          <label className="block text-sm font-medium text-blue-200 mb-2">
            Brand Name *
          </label>
          <input
            type="text"
            value={formData.brand_name}
            onChange={(e) => handleChange('brand_name', e.target.value)}
            className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-blue-300 focus:outline-none focus:border-blue-400"
            placeholder="Enter your brand name"
            disabled={disabled}
            required
          />
        </div>
        
        {/* Target Audience */}
        <div>
          <label className="block text-sm font-medium text-blue-200 mb-2">
            Target Audience
          </label>
          <select
            value={formData.target_audience}
            onChange={(e) => handleChange('target_audience', e.target.value)}
            className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-blue-400"
            disabled={disabled}
          >
            <option value="general audience">General Audience</option>
            <option value="young adults">Young Adults (18-30)</option>
            <option value="professionals">Professionals</option>
            <option value="parents">Parents</option>
            <option value="seniors">Seniors (55+)</option>
            <option value="entrepreneurs">Entrepreneurs</option>
          </select>
        </div>
      </div>
      
      {/* Brand Description */}
      <div>
        <label className="block text-sm font-medium text-blue-200 mb-2">
          Brand Description *
        </label>
        <textarea
          value={formData.brand_description}
          onChange={(e) => handleChange('brand_description', e.target.value)}
          className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-blue-300 focus:outline-none focus:border-blue-400"
          placeholder="Describe your brand, product, or service..."
          rows={4}
          disabled={disabled}
          required
        />
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Tone */}
        <div>
          <label className="block text-sm font-medium text-blue-200 mb-2">
            Tone
          </label>
          <select
            value={formData.tone}
            onChange={(e) => handleChange('tone', e.target.value)}
            className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-blue-400"
            disabled={disabled}
          >
            <option value="friendly">Friendly</option>
            <option value="professional">Professional</option>
            <option value="energetic">Energetic</option>
            <option value="sophisticated">Sophisticated</option>
            <option value="casual">Casual</option>
          </select>
        </div>
        
        {/* Duration */}
        <div>
          <label className="block text-sm font-medium text-blue-200 mb-2">
            Duration (seconds)
          </label>
          <select
            value={formData.duration}
            onChange={(e) => handleChange('duration', parseInt(e.target.value))}
            className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-blue-400"
            disabled={disabled}
          >
            <option value={15}>15 seconds</option>
            <option value={30}>30 seconds</option>
            <option value={45}>45 seconds</option>
            <option value={60}>60 seconds</option>
          </select>
        </div>
        
        {/* Call to Action */}
        <div>
          <label className="block text-sm font-medium text-blue-200 mb-2">
            Call to Action
          </label>
          <input
            type="text"
            value={formData.call_to_action}
            onChange={(e) => handleChange('call_to_action', e.target.value)}
            className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-blue-300 focus:outline-none focus:border-blue-400"
            placeholder="Call to action text"
            disabled={disabled}
          />
        </div>
      </div>
      
      {/* Error Message */}
      {error && (
        <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4">
          <p className="text-red-200">{error}</p>
        </div>
      )}
      
      {/* Submit Button */}
      <button
        type="submit"
        disabled={disabled || isSubmitting}
        className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold py-4 px-8 rounded-lg transition-all duration-200 disabled:cursor-not-allowed"
      >
        {isSubmitting ? 'Starting Generation...' : 'Generate Video Ad'}
      </button>
    </form>
  )
}