import React from 'react'
import { VideoGenerator } from './components/VideoGenerator'
import { JobStatus } from './components/JobStatus'
import './App.css'

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            Relicon
          </h1>
          <p className="text-xl text-blue-200">
            AI-Powered Video Ad Generation Platform
          </p>
        </header>
        
        <main className="max-w-4xl mx-auto">
          <VideoGenerator />
        </main>
      </div>
    </div>
  )
}