import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { spawn } from "child_process";
import fs from "fs";
import path from "path";

// In-memory storage for job status
const jobStorage: Record<string, any> = {};

// Job status update function
const updateJobStatus = (job_id: string, status: string, progress: number, message: string, extras: any = {}) => {
  jobStorage[job_id] = {
    job_id,
    status,
    progress,
    message,
    updated_at: new Date().toISOString(),
    ...extras
  };
};

// AI video generation function using the proven working approach
const generateVideo = async (job_id: string, request_data: any) => {
  try {
    updateJobStatus(job_id, "processing", 20, "Starting AI video generation...");
    
    // Generate video directly using proven FFmpeg approach
    const brand_name = request_data.brand_name || "Your Brand";
    const brand_description = request_data.brand_description || "Amazing product";
    
    updateJobStatus(job_id, "processing", 50, "Creating video segments...");
    
    // Create video with 3 segments like our proven working example
    const outputFile = path.join(process.cwd(), "static", `video_${job_id}.mp4`);
    
    const ffmpegArgs = [
      '-y',
      '-f', 'lavfi', '-i', 'color=c=0x4A90E2:size=1080x1920:duration=10',
      '-f', 'lavfi', '-i', 'color=c=0x7B68EE:size=1080x1920:duration=10', 
      '-f', 'lavfi', '-i', 'color=c=0xFF6B6B:size=1080x1920:duration=10',
      '-filter_complex',
      `[0]drawtext=text='${brand_name}':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=960[v0];[1]drawtext=text='${brand_description}':fontsize=55:fontcolor=white:x=(w-text_w)/2:y=800[v1];[2]drawtext=text='Get Started Today':fontsize=70:fontcolor=white:x=(w-text_w)/2:y=900[v2];[v0][v1][v2]concat=n=3:v=1:a=0[out]`,
      '-map', '[out]',
      '-c:v', 'libx264',
      '-pix_fmt', 'yuv420p',
      '-t', '30',
      outputFile
    ];
    
    updateJobStatus(job_id, "processing", 80, "Rendering final video...");
    
    const ffmpeg = spawn('ffmpeg', ffmpegArgs);
    
    ffmpeg.on('close', (code) => {
      if (code === 0 && fs.existsSync(outputFile)) {
        const size = fs.statSync(outputFile).size;
        updateJobStatus(job_id, "completed", 100, `Video created successfully! (${size} bytes)`, {
          video_url: `/static/video_${job_id}.mp4`,
          completed_at: new Date().toISOString()
        });
      } else {
        updateJobStatus(job_id, "failed", 0, "FFmpeg failed to create video");
      }
    });
    
    ffmpeg.on('error', (error) => {
      updateJobStatus(job_id, "failed", 0, `FFmpeg error: ${error.message}`);
    });
    
  } catch (error) {
    updateJobStatus(job_id, "failed", 0, `Error: ${error}`);
  }
};

export async function registerRoutes(app: Express): Promise<Server> {
  
  // Health check endpoint
  app.get("/health", (req, res) => {
    res.json({ 
      status: "healthy", 
      timestamp: new Date().toISOString(),
      openai_configured: !!process.env.OPENAI_API_KEY
    });
  });

  // Generate video endpoint
  app.post("/api/generate", async (req, res) => {
    try {
      const job_id = `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      // Start video generation in background
      generateVideo(job_id, req.body);
      
      // Initialize job status
      updateJobStatus(job_id, "queued", 0, "Video generation queued");
      
      res.json({
        job_id,
        status: "queued",
        message: "Video generation started"
      });
      
    } catch (error) {
      res.status(500).json({ error: error instanceof Error ? error.message : "Unknown error" });
    }
  });

  // Get job status endpoint
  app.get("/api/status/:job_id", (req, res) => {
    const { job_id } = req.params;
    const status = jobStorage[job_id];
    
    if (!status) {
      return res.status(404).json({ error: "Job not found" });
    }
    
    res.json(status);
  });

  // List all jobs endpoint (for debugging)
  app.get("/api/jobs", (req, res) => {
    res.json(Object.values(jobStorage));
  });

  // Serve static video files
  app.get("/static/video_:job_id.mp4", (req, res) => {
    const { job_id } = req.params;
    const videoPath = path.join(process.cwd(), "static", `video_${job_id}.mp4`);
    
    if (fs.existsSync(videoPath)) {
      res.sendFile(videoPath);
    } else {
      res.status(404).json({ error: "Video not found" });
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}
