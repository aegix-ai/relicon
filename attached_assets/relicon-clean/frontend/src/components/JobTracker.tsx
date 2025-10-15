import React, { useState, useEffect } from 'react'

interface JobTrackerProps {
  jobId: string
  onCompleted: () => void
}

interface JobStatus {
  job_id: string
  status: string
  progress: number
  message: string
  video_url?: string
}

export function JobTracker({ jobId, onCompleted }: JobTrackerProps) {
  const [status, setStatus] = useState<JobStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await fetch(`/api/status/${jobId}`)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        setStatus(data)
        
        if (data.status === 'completed' || data.status === 'failed') {
          if (data.status === 'completed') {
            onCompleted()
          }
          return // Stop polling
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch status')
      }
    }
    
    // Poll immediately
    pollStatus()
    
    // Then poll every 2 seconds
    const interval = setInterval(pollStatus, 2000)
    
    return () => clearInterval(interval)
  }, [jobId, onCompleted])
  
  if (error) {
    return (
      <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-6">
        <h3 className="text-lg font-bold text-red-200 mb-2">Error</h3>
        <p className="text-red-200">{error}</p>
      </div>
    )
  }
  
  if (!status) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
        <span className="ml-3 text-blue-200">Loading status...</span>
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      {/* Job Info */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white">Job: {status.job_id}</h3>
          <p className="text-blue-200">Status: {status.status}</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-white">{status.progress}%</div>
          <div className="text-sm text-blue-200">
            {status.status === 'completed' ? 'Completed' : 
             status.status === 'failed' ? 'Failed' : 
             status.status === 'processing' ? 'In Progress' : 'Queued'}
          </div>
        </div>
      </div>
      
      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-blue-200">Progress</span>
          <span className="text-sm font-bold text-white">{status.progress}% Complete</span>
        </div>
        <div className="w-full bg-white/10 rounded-full h-4 shadow-inner">
          <div 
            className="bg-gradient-to-r from-blue-500 to-purple-500 h-4 rounded-full transition-all duration-500 ease-out shadow-lg"
            style={{ width: `${status.progress}%` }}
          >
            <div className="w-full h-full bg-white/20 rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>
      
      {/* Current Message */}
      <div className="bg-white/5 rounded-lg p-4">
        <p className="text-blue-200">{status.message}</p>
      </div>
      
      {/* Status Indicators */}
      <div className="grid grid-cols-4 gap-4">
        <StatusStep 
          title="Planning" 
          active={status.progress >= 10}
          completed={status.progress >= 20}
        />
        <StatusStep 
          title="Generating" 
          active={status.progress >= 20}
          completed={status.progress >= 70}
        />
        <StatusStep 
          title="Audio + Music" 
          active={status.progress >= 70}
          completed={status.progress >= 85}
        />
        <StatusStep 
          title="Final Assembly" 
          active={status.progress >= 85}
          completed={status.progress >= 100}
        />
      </div>
      
      {/* Download Button */}
      {status.status === 'completed' && status.video_url && (
        <div className="text-center">
          <a
            href={status.video_url}
            download
            className="inline-block bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-bold py-4 px-8 rounded-lg transition-all duration-200"
          >
            Download Your Video
          </a>
        </div>
      )}
      
      {/* Failure State */}
      {status.status === 'failed' && (
        <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-6 text-center">
          <h3 className="text-lg font-bold text-red-200 mb-2">Generation Failed</h3>
          <p className="text-red-200">{status.message}</p>
        </div>
      )}
    </div>
  )
}

interface StatusStepProps {
  title: string
  active: boolean
  completed: boolean
}

function StatusStep({ title, active, completed }: StatusStepProps) {
  return (
    <div className={`text-center p-3 rounded-lg border ${
      completed 
        ? 'bg-green-500/20 border-green-500/50 text-green-200'
        : active 
          ? 'bg-blue-500/20 border-blue-500/50 text-blue-200'
          : 'bg-white/5 border-white/20 text-gray-400'
    }`}>
      <div className={`w-4 h-4 rounded-full mx-auto mb-2 ${
        completed 
          ? 'bg-green-500'
          : active 
            ? 'bg-blue-500 animate-pulse'
            : 'bg-gray-600'
      }`}></div>
      <div className="text-xs font-medium">{title}</div>
    </div>
  )
}