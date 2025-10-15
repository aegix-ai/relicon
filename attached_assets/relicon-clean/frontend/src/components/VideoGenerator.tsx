import React, { useState } from 'react'
import { VideoForm } from './VideoForm'
import { JobTracker } from './JobTracker'

export function VideoGenerator() {
  const [currentJob, setCurrentJob] = useState<string | null>(null)
  
  const handleJobCreated = (jobId: string) => {
    setCurrentJob(jobId)
  }
  
  const handleJobCompleted = () => {
    setCurrentJob(null)
  }
  
  return (
    <div className="space-y-8">
      {/* Video Generation Form */}
      <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
        <h2 className="text-2xl font-bold text-white mb-6">
          Generate Your Video Ad
        </h2>
        <VideoForm 
          onJobCreated={handleJobCreated}
          disabled={currentJob !== null}
        />
      </div>
      
      {/* Job Progress Tracker */}
      {currentJob && (
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-6">
            Generation Progress
          </h2>
          <JobTracker 
            jobId={currentJob}
            onCompleted={handleJobCompleted}
          />
        </div>
      )}
    </div>
  )
}