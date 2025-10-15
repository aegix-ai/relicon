"use client"

import { useState } from 'react'
import JobTracker from '../components/JobTracker'

export default function Home() {
  const [brand, setBrand] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          brand_name: brand,
          brand_description: description,
          duration: 30
        })
      })
      
      const data = await response.json()
      setResult(data)
      
      // Poll for status updates
      if (data.job_id) {
        const pollStatus = setInterval(async () => {
          const statusResponse = await fetch(`/api/status/${data.job_id}`)
          const statusData = await statusResponse.json()
          setResult(statusData)
          
          if (statusData.status === 'completed' || statusData.status === 'failed') {
            clearInterval(pollStatus)
            setLoading(false)
          }
        }, 2000)
      }
    } catch (error) {
      console.error('Error:', error)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 to-purple-900 p-8">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            Relicon Clean System
          </h1>
          <p className="text-xl text-blue-200">
            AI-Powered Video Generation - Clean Architecture
          </p>
          <div className="text-sm text-green-400 mt-2 font-mono">
            ✓ Running from relicon/ directory
          </div>
        </header>

        <div className="bg-white/10 backdrop-blur-md rounded-lg p-8 shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-white text-sm font-medium mb-2">
                Brand Name
              </label>
              <input
                type="text"
                value={brand}
                onChange={(e) => setBrand(e.target.value)}
                className="w-full px-4 py-3 bg-white/20 text-white placeholder-white/60 border border-white/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
                placeholder="Enter your brand name"
                required
              />
            </div>

            <div>
              <label className="block text-white text-sm font-medium mb-2">
                Brand Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                className="w-full px-4 py-3 bg-white/20 text-white placeholder-white/60 border border-white/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
                placeholder="Describe your brand and what makes it special"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {loading ? 'Generating Video...' : 'Generate Video'}
            </button>
          </form>

          {result && (
            <div className="mt-8">
              <JobTracker jobId={result.job_id} />
            </div>
          )}
        </div>

        <div className="mt-8 text-center text-white/60 text-sm">
          <p>Powered by Clean Relicon-Rewrite Architecture</p>
          <p>Cost: $2.42-4.80 per video | Duration: 30 seconds | 3 scenes</p>
        </div>
      </div>
    </div>
  )
}