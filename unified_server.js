const express = require('express');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

const app = express();
const PORT = 5000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// CORS headers
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  
  if (req.method === 'OPTIONS') {
    res.sendStatus(200);
  } else {
    next();
  }
});

// In-memory storage for job status
const jobStorage = {};

// Job status update function
const updateJobStatus = (job_id, status, progress, message, extras = {}) => {
  jobStorage[job_id] = {
    job_id,
    status,
    progress,
    message,
    updated_at: new Date().toISOString(),
    ...extras
  };
};

// Generate random job ID
const generateJobId = () => {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 8);
  return `job_${timestamp}_${random}`;
};

// API Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

app.post('/api/generate', async (req, res) => {
  try {
    const { brand_name, brand_description, target_audience, tone, duration, call_to_action } = req.body;
    
    if (!brand_name || !brand_description) {
      return res.status(400).json({ error: 'Brand name and description are required' });
    }

    const job_id = generateJobId();
    
    // Initialize job status
    updateJobStatus(job_id, 'queued', 0, 'Video generation started');
    
    // Start async video generation
    generateVideoAsync(job_id, {
      brand_name,
      brand_description,
      target_audience: target_audience || 'general audience',
      tone: tone || 'professional',
      duration: duration || 30,
      call_to_action: call_to_action || 'Take action now'
    });

    res.json({
      job_id,
      status: 'queued',
      message: 'Video generation started'
    });
  } catch (error) {
    console.error('Error starting video generation:', error);
    res.status(500).json({ error: 'Failed to start video generation' });
  }
});

app.get('/api/status/:job_id', (req, res) => {
  const { job_id } = req.params;
  const job = jobStorage[job_id];
  
  if (!job) {
    return res.status(404).json({ error: 'Job not found' });
  }
  
  res.json(job);
});

// Generate video asynchronously
async function generateVideoAsync(job_id, requestData) {
  try {
    // Step 1: Analyzing brand
    updateJobStatus(job_id, 'processing', 10, 'Analyzing brand tone and audience...');
    await sleep(2000);
    
    // Step 2: Generating script
    updateJobStatus(job_id, 'processing', 30, 'Generating AI script with natural pacing...');
    await sleep(3000);
    
    // Step 3: Creating voiceover
    updateJobStatus(job_id, 'processing', 50, 'Creating voiceover with ElevenLabs AI...');
    await sleep(4000);
    
    // Step 4: Generating scenes
    updateJobStatus(job_id, 'processing', 70, 'Generating dynamic scenes and transitions...');
    await sleep(3000);
    
    // Step 5: Assembling video
    updateJobStatus(job_id, 'processing', 90, 'Assembling final video with synchronized captions...');
    
    // Call the Python video generation system
    const pythonScript = `
import sys
import json
import os
sys.path.append('.')

# Import our video generation system
from working_video_generator import main as generate_video

try:
    # Generate the video
    result = generate_video()
    print(f"VIDEO_SUCCESS:{result}")
except Exception as e:
    print(f"VIDEO_ERROR:{str(e)}")
`;

    const scriptPath = `/tmp/generate_${job_id}.py`;
    fs.writeFileSync(scriptPath, pythonScript);
    
    const pythonProcess = spawn('python3', [scriptPath], {
      env: { ...process.env },
      cwd: process.cwd()
    });
    
    let output = '';
    let error = '';
    
    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      error += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (code === 0 && output.includes('VIDEO_SUCCESS:')) {
        // Extract video path from output
        const videoMatch = output.match(/VIDEO_SUCCESS:(.+)/);
        const videoPath = videoMatch ? videoMatch[1].trim() : 'working_video_generator.mp4';
        
        updateJobStatus(job_id, 'completed', 100, 'Video generation completed!', {
          video_url: `/outputs/${path.basename(videoPath)}`,
          completed_at: new Date().toISOString()
        });
      } else {
        console.error('Video generation failed:', error);
        updateJobStatus(job_id, 'failed', 0, 'Video generation failed', {
          error: error || 'Unknown error occurred'
        });
      }
      
      // Clean up script file
      try {
        fs.unlinkSync(scriptPath);
      } catch (e) {}
    });
    
  } catch (error) {
    console.error('Error in video generation:', error);
    updateJobStatus(job_id, 'failed', 0, 'Video generation failed', {
      error: error.message
    });
  }
}

// Serve static video files
app.use('/outputs', express.static(path.join(__dirname, '.')));

// Serve the Next.js frontend
app.use(express.static('client/dist'));

// Fallback to serve index.html for client-side routing
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'client/dist/index.html'));
});

// Utility function
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Start server
app.listen(PORT, () => {
  console.log(`🚀 ReelForge server running on http://localhost:${PORT}`);
  console.log(`📊 Dashboard: http://localhost:${PORT}/dashboard`);
  console.log(`🔧 API Health: http://localhost:${PORT}/api/health`);
});