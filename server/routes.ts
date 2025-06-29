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

// Enhanced AI video generation with comprehensive planning and audio
const generateVideo = async (job_id: string, request_data: any) => {
  try {
    const { brand_name, brand_description, target_audience, tone, duration, call_to_action } = request_data;
    
    updateJobStatus(job_id, "processing", 5, "AI analyzing brand and market positioning...");
    
    // Step 1: Comprehensive AI Planning
    const planningScript = `
import os
import json
from openai import OpenAI

openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Comprehensive AI planning
brand_name = """${brand_name}"""
brand_description = """${brand_description}"""
target_audience = """${target_audience || 'general audience'}"""
tone = """${tone || 'professional'}"""
call_to_action = """${call_to_action || 'Learn more'}"""

# Multi-stage AI planning
planning_prompt = f"""You are a world-class creative director and video strategist. Create a comprehensive, detailed video plan for {brand_name}.

Brand Details:
- Name: {brand_name}
- Description: {brand_description}
- Target Audience: {target_audience}
- Tone: {tone}
- Call to Action: {call_to_action}

Create an exhaustive plan with these sections:

1. STRATEGIC ANALYSIS (500+ words)
   - Market positioning analysis
   - Competitive landscape insights
   - Audience psychology breakdown
   - Emotional triggers identification
   - Brand voice refinement

2. CREATIVE CONCEPT (300+ words)
   - Core message strategy
   - Storytelling narrative arc
   - Visual style direction
   - Pacing and rhythm strategy

3. DETAILED SCRIPT (5 segments, each 6 seconds)
   - Hook (grab attention instantly)
   - Problem identification
   - Solution presentation
   - Benefit demonstration
   - Strong call-to-action

4. TECHNICAL SPECIFICATIONS
   - Visual elements for each segment
   - Color palette with hex codes
   - Typography specifications
   - Transition recommendations

Return ONLY valid JSON:
{
  "strategic_analysis": "detailed analysis...",
  "creative_concept": "detailed concept...",
  "script_segments": [
    {"segment": 1, "voiceover": "compelling text", "visual_hint": "description", "duration": 6},
    {"segment": 2, "voiceover": "compelling text", "visual_hint": "description", "duration": 6},
    {"segment": 3, "voiceover": "compelling text", "visual_hint": "description", "duration": 6},
    {"segment": 4, "voiceover": "compelling text", "visual_hint": "description", "duration": 6},
    {"segment": 5, "voiceover": "compelling text", "visual_hint": "description", "duration": 6}
  ],
  "technical_specs": {
    "colors": ["#4A90E2", "#7B68EE", "#FF6B6B", "#50C878", "#FFD700"],
    "transitions": ["fade", "slide", "zoom", "crossfade"],
    "visual_style": "modern minimalist"
  }
}"""

try:
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": planning_prompt}],
        response_format={"type": "json_object"}
    )
    plan = json.loads(response.choices[0].message.content)
    print(f"PLAN_SUCCESS:{json.dumps(plan)}")
except Exception as e:
    print(f"PLAN_ERROR:{str(e)}")
`;

    updateJobStatus(job_id, "processing", 15, "Generating comprehensive creative strategy...");
    
    // Execute planning script
    const planPath = `/tmp/plan_${job_id}.py`;
    fs.writeFileSync(planPath, planningScript);
    
    const planning = spawn('python', [planPath], { env: { ...process.env } });
    let planOutput = '';
    
    planning.stdout.on('data', (data) => { planOutput += data.toString(); });
    
    await new Promise((resolve, reject) => {
      planning.on('close', async (code) => {
        fs.unlinkSync(planPath);
        
        if (!planOutput.includes('PLAN_SUCCESS:')) {
          updateJobStatus(job_id, "failed", 0, "AI planning failed");
          return reject(new Error("Planning failed"));
        }
        
        const planData = JSON.parse(planOutput.split('PLAN_SUCCESS:')[1]);
        
        updateJobStatus(job_id, "processing", 30, "Creating professional voiceovers...");
        
        // Step 2: Generate Audio for each segment
        const audioFiles = [];
        for (let i = 0; i < planData.script_segments.length; i++) {
          const segment = planData.script_segments[i];
          const audioFile = path.join(process.cwd(), "static", `audio_${job_id}_${i}.mp3`);
          
          const audioScript = `
import os
from openai import OpenAI

openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

text = """${segment.voiceover}"""
voice_tone = "${tone}"

# Select voice based on tone
voice_map = {
    "professional": "nova", 
    "casual": "alloy",
    "energetic": "shimmer",
    "friendly": "echo"
}
voice = voice_map.get(voice_tone, "nova")

try:
    response = openai.audio.speech.create(
        model="tts-1-hd",
        voice=voice,
        input=text,
        speed=1.0
    )
    response.stream_to_file("${audioFile}")
    print(f"AUDIO_SUCCESS:${audioFile}")
except Exception as e:
    print(f"AUDIO_ERROR:{str(e)}")
`;
          
          const audioPath = `/tmp/audio_${job_id}_${i}.py`;
          fs.writeFileSync(audioPath, audioScript);
          
          const audio = spawn('python', [audioPath], { env: { ...process.env } });
          let audioOutput = '';
          
          audio.stdout.on('data', (data) => { audioOutput += data.toString(); });
          
          await new Promise((audioResolve) => {
            audio.on('close', (code) => {
              fs.unlinkSync(audioPath);
              if (audioOutput.includes('AUDIO_SUCCESS:')) {
                audioFiles.push(audioFile);
              }
              audioResolve(null);
            });
          });
        }
        
        updateJobStatus(job_id, "processing", 60, "Assembling video with synchronized audio...");
        
        // Step 3: Create Video with Audio
        const outputFile = path.join(process.cwd(), "static", `video_${job_id}.mp4`);
        const colors = planData.technical_specs.colors || ['#4A90E2', '#7B68EE', '#FF6B6B', '#50C878', '#FFD700'];
        
        // Build complex FFmpeg command with audio
        let ffmpegArgs = ['-y'];
        let filterComplex = '';
        
        // Add video inputs
        planData.script_segments.forEach((segment, i) => {
          const color = colors[i % colors.length].replace('#', '0x');
          ffmpegArgs.push('-f', 'lavfi', '-i', `color=c=${color}:size=1080x1920:duration=${segment.duration}`);
        });
        
        // Add audio inputs
        audioFiles.forEach(file => {
          if (fs.existsSync(file)) {
            ffmpegArgs.push('-i', file);
          }
        });
        
        // Build filter complex for video with text
        const videoFilters = planData.script_segments.map((segment, i) => {
          const text = segment.voiceover.replace(/['"]/g, '').substring(0, 50);
          return `[${i}]drawtext=text='${text}':fontsize=40:fontcolor=white:x=(w-text_w)/2:y=960:enable='between(t,0,${segment.duration})'[v${i}]`;
        }).join(';');
        
        // Concatenate videos
        const videoInputs = planData.script_segments.map((_, i) => `[v${i}]`).join('');
        const videoConcat = `${videoInputs}concat=n=${planData.script_segments.length}:v=1:a=0[video]`;
        
        // Mix audio
        const audioInputStart = planData.script_segments.length;
        const audioMix = audioFiles.length > 0 ? 
          `;${audioFiles.map((_, i) => `[${audioInputStart + i}]`).join('')}concat=n=${audioFiles.length}:v=0:a=1[audio]` : '';
        
        filterComplex = videoFilters + ';' + videoConcat + audioMix;
        
        ffmpegArgs.push(
          '-filter_complex', filterComplex,
          '-map', '[video]'
        );
        
        if (audioFiles.length > 0) {
          ffmpegArgs.push('-map', '[audio]');
        }
        
        ffmpegArgs.push(
          '-c:v', 'libx264',
          '-c:a', 'aac',
          '-pix_fmt', 'yuv420p',
          '-r', '30',
          outputFile
        );
        
        updateJobStatus(job_id, "processing", 85, "Final video assembly...");
        
        const ffmpeg = spawn('ffmpeg', ffmpegArgs);
        
        ffmpeg.on('close', (code) => {
          // Clean up audio files
          audioFiles.forEach(file => {
            if (fs.existsSync(file)) fs.unlinkSync(file);
          });
          
          if (code === 0 && fs.existsSync(outputFile)) {
            const size = fs.statSync(outputFile).size;
            updateJobStatus(job_id, "completed", 100, `Professional video with AI voiceover created! (${size} bytes)`, {
              video_url: `/static/video_${job_id}.mp4`,
              completed_at: new Date().toISOString(),
              plan_summary: planData.creative_concept.substring(0, 200) + "..."
            });
          } else {
            updateJobStatus(job_id, "failed", 0, "Video assembly failed");
          }
        });
        
        ffmpeg.on('error', (error) => {
          updateJobStatus(job_id, "failed", 0, `Assembly error: ${error.message}`);
        });
        
        resolve(null);
      });
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
