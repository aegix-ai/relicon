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

// AI video generation function
const generateVideo = async (job_id: string, request_data: any) => {
  try {
    updateJobStatus(job_id, "processing", 10, "Starting AI video generation...");
    
    // Create a Python script to handle video generation
    const scriptContent = `
import os
import json
import subprocess
from openai import OpenAI

# Initialize OpenAI
openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_video():
    try:
        # Generate AI concept and script
        brand_name = "${request_data.brand_name}"
        brand_description = "${request_data.brand_description}"
        
        prompt = f"""Create a viral short-form video concept for {brand_name}: {brand_description}

Generate a JSON response with:
1. A hook (opening line to grab attention)
2. 3 script segments, each 8-10 seconds long

Format:
{
  "hook": "compelling opening line",
  "segments": [
    {"text": "voiceover text", "duration": 8},
    {"text": "voiceover text", "duration": 9},
    {"text": "voiceover text", "duration": 10}
  ]
}

Make it engaging and thumb-stopping for social media."""

        response = openai.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        script_data = json.loads(response.choices[0].message.content)
        
        # Create video using FFmpeg
        import os
        os.makedirs("static", exist_ok=True)
        output_file = f"static/video_{job_id}.mp4"
        segments = script_data['segments']
        colors = ['0x4A90E2', '0x7B68EE', '0xFF6B6B']
        
        # Build FFmpeg command
        inputs = []
        filter_parts = []
        
        for i, segment in enumerate(segments):
            duration = segment.get('duration', 8)
            text = segment.get('text', f'Segment {i+1}')
            
            # Clean text for FFmpeg - more thorough sanitization
            safe_text = text.replace("'", "").replace('"', "").replace(":", "").replace(",", "")
            safe_text = safe_text.replace("(", "").replace(")", "").replace("!", "")
            safe_text = safe_text.replace("?", "").replace("&", "and").replace("#", "")
            safe_text = safe_text.replace("\\", "").replace("/", "").replace("*", "")
            if len(safe_text) > 40:
                safe_text = safe_text[:37] + "..."
            
            color = colors[i % len(colors)]
            
            # Add input
            inputs.extend(['-f', 'lavfi', '-i', f'color=c={color}:size=1080x1920:duration={duration}'])
            
            # Add text overlay
            y_pos = 960 if i % 2 == 0 else 800
            filter_parts.append(f'[{i}]drawtext=text={safe_text}:fontsize=48:fontcolor=white:x=(w-text_w)/2:y={y_pos}[v{i}]')
        
        # Concatenate all segments
        concat_inputs = ''.join(f'[v{i}]' for i in range(len(segments)))
        filter_parts.append(f'{concat_inputs}concat=n={len(segments)}:v=1:a=0[out]')
        
        # Complete FFmpeg command
        cmd = ['ffmpeg', '-y'] + inputs + [
            '-filter_complex', ';'.join(filter_parts),
            '-map', '[out]',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', '30',
            output_file
        ]
        
        # Execute FFmpeg with better error handling
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and os.path.exists(output_file):
                size = os.path.getsize(output_file)
                print(f"SUCCESS:{output_file}:{size}")
            else:
                print(f"ERROR:FFmpeg failed with return code {result.returncode}")
                print(f"ERROR:STDERR: {result.stderr}")
                print(f"ERROR:STDOUT: {result.stdout}")
        except subprocess.TimeoutExpired:
            print("ERROR:FFmpeg timeout after 120 seconds")
        except Exception as e:
            print(f"ERROR:FFmpeg execution failed: {str(e)}")
            
    except Exception as e:
        print(f"ERROR:{str(e)}")

if __name__ == "__main__":
    generate_video()
`;

    // Write the script to a temporary file
    const scriptPath = `/tmp/generate_${job_id}.py`;
    fs.writeFileSync(scriptPath, scriptContent);
    
    updateJobStatus(job_id, "processing", 30, "Generating AI concept...");
    
    // Execute the Python script
    const python = spawn('python', [scriptPath], {
      env: { ...process.env }
    });
    
    let output = '';
    let errorOutput = '';
    
    python.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    python.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });
    
    python.on('close', (code) => {
      // Clean up script file
      try {
        fs.unlinkSync(scriptPath);
      } catch (e) {
        // Ignore cleanup errors
      }
      
      console.log(`Python script finished with code ${code}`);
      console.log(`Output: ${output}`);
      console.log(`Error Output: ${errorOutput}`);
      
      if (code === 0 && output.includes('SUCCESS:')) {
        const parts = output.split(':');
        const videoFile = parts[1];
        const size = parts[2];
        
        updateJobStatus(job_id, "completed", 100, `Video created successfully! (${size} bytes)`, {
          video_url: `/static/video_${job_id}.mp4`,
          completed_at: new Date().toISOString()
        });
      } else {
        const errorMsg = errorOutput || output || 'Unknown error';
        updateJobStatus(job_id, "failed", 0, `Video generation failed: ${errorMsg}`);
      }
    });
    
    updateJobStatus(job_id, "processing", 80, "Rendering final video...");
    
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
