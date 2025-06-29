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
    
    updateJobStatus(job_id, "processing", 10, "AI creating comprehensive strategy...");
    
    // Step 1: Use Node.js for AI planning
    updateJobStatus(job_id, "processing", 15, "Initializing AI systems...");
    
    // Create a simplified approach that works reliably
    const script = `
import os
import json
from openai import OpenAI

openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

brand = "${brand_name}"
desc = "${brand_description}"

prompt = f"""Create a detailed video plan for {brand}: {desc}

Return JSON with 5 script segments:
{{
  "segments": [
    {{"text": "Hook: compelling opener", "duration": 6}},
    {{"text": "Problem: identify issue", "duration": 6}},
    {{"text": "Solution: show benefit", "duration": 6}}, 
    {{"text": "Proof: demonstrate value", "duration": 6}},
    {{"text": "CTA: strong call to action", "duration": 6}}
  ]
}}"""

try:
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{{"role": "user", "content": prompt}}],
        response_format={{"type": "json_object"}}
    )
    result = json.loads(response.choices[0].message.content)
    print("SCRIPT_SUCCESS:" + json.dumps(result))
except Exception as e:
    print("SCRIPT_ERROR:" + str(e))
`;

    const scriptPath = `/tmp/simple_${job_id}.py`;
    fs.writeFileSync(scriptPath, script);
    
    const python = spawn('python', [scriptPath], { env: { ...process.env } });
    let output = '';
    
    python.stdout.on('data', (data) => { output += data.toString(); });
    
    await new Promise((resolve) => {
      python.on('close', async (code) => {
        fs.unlinkSync(scriptPath);
        
        if (!output.includes('SCRIPT_SUCCESS:')) {
          updateJobStatus(job_id, "failed", 0, "AI script generation failed");
          return resolve(null);
        }
        
        const scriptData = JSON.parse(output.split('SCRIPT_SUCCESS:')[1]);
        
        updateJobStatus(job_id, "processing", 40, "Creating professional voiceovers...");
        
        // Step 2: Generate Audio for each segment
        const audioFiles: string[] = [];
        const voiceMap: { [key: string]: string } = {
          professional: "nova",
          casual: "alloy", 
          energetic: "shimmer",
          friendly: "echo"
        };
        const selectedVoice = voiceMap[tone as string] || "nova";
        
        for (let i = 0; i < scriptData.segments.length; i++) {
          const segment = scriptData.segments[i];
          const audioFile = path.join(process.cwd(), "static", `audio_${job_id}_${i}.mp3`);
          
          const audioScript = `
import os
from openai import OpenAI

openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

text = """${segment.text}"""

try:
    response = openai.audio.speech.create(
        model="tts-1-hd",
        voice="${selectedVoice}",
        input=text,
        speed=1.0
    )
    response.stream_to_file("${audioFile}")
    print("AUDIO_SUCCESS:${audioFile}")
except Exception as e:
    print("AUDIO_ERROR:" + str(e))
`;
          
          const audioPath = `/tmp/audio_${job_id}_${i}.py`;
          fs.writeFileSync(audioPath, audioScript);
          
          const audio = spawn('python', [audioPath], { env: { ...process.env } });
          let audioOutput = '';
          
          audio.stdout.on('data', (data: any) => { audioOutput += data.toString(); });
          
          await new Promise((audioResolve) => {
            audio.on('close', () => {
              fs.unlinkSync(audioPath);
              if (audioOutput.includes('AUDIO_SUCCESS:')) {
                audioFiles.push(audioFile);
              }
              audioResolve(null);
            });
          });
          
          updateJobStatus(job_id, "processing", 40 + (i + 1) * 6, `Generated voiceover ${i + 1}/5...`);
        }
        
        updateJobStatus(job_id, "processing", 75, "Assembling video with synchronized audio...");
        
        // Step 3: Create Video with Audio
        const outputFile = path.join(process.cwd(), "static", `video_${job_id}.mp4`);
        const colors = ['#4A90E2', '#7B68EE', '#FF6B6B', '#50C878', '#FFD700'];
        
        // Build FFmpeg command with audio
        let ffmpegArgs = ['-y'];
        
        // Add video inputs
        scriptData.segments.forEach((segment: any, i: number) => {
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
        const videoFilters = scriptData.segments.map((segment: any, i: number) => {
          const text = segment.text.replace(/['"]/g, '').substring(0, 50);
          return `[${i}]drawtext=text='${text}':fontsize=40:fontcolor=white:x=(w-text_w)/2:y=960[v${i}]`;
        }).join(';');
        
        // Concatenate videos
        const videoInputs = scriptData.segments.map((_: any, i: number) => `[v${i}]`).join('');
        const videoConcat = `${videoInputs}concat=n=${scriptData.segments.length}:v=1:a=0[video]`;
        
        // Mix audio if available
        const audioInputStart = scriptData.segments.length;
        const audioMix = audioFiles.length > 0 ? 
          `;${audioFiles.map((_, i) => `[${audioInputStart + i}]`).join('')}concat=n=${audioFiles.length}:v=0:a=1[audio]` : '';
        
        const filterComplex = videoFilters + ';' + videoConcat + audioMix;
        
        ffmpegArgs.push('-filter_complex', filterComplex, '-map', '[video]');
        
        if (audioFiles.length > 0) {
          ffmpegArgs.push('-map', '[audio]');
        }
        
        ffmpegArgs.push('-c:v', 'libx264', '-c:a', 'aac', '-pix_fmt', 'yuv420p', '-r', '30', outputFile);
        
        updateJobStatus(job_id, "processing", 85, "Final video assembly...");
        
        const ffmpeg = spawn('ffmpeg', ffmpegArgs);
        
        ffmpeg.on('close', (code: number) => {
          // Clean up audio files
          audioFiles.forEach(file => {
            if (fs.existsSync(file)) fs.unlinkSync(file);
          });
          
          if (code === 0 && fs.existsSync(outputFile)) {
            const size = fs.statSync(outputFile).size;
            updateJobStatus(job_id, "completed", 100, `AI video with professional voiceover created! (${size} bytes)`, {
              video_url: `/static/video_${job_id}.mp4`,
              completed_at: new Date().toISOString()
            });
          } else {
            updateJobStatus(job_id, "failed", 0, "Video assembly failed");
          }
        });
        
        ffmpeg.on('error', (error: any) => {
          updateJobStatus(job_id, "failed", 0, `Assembly error: ${error.message}`);
        });
        
        resolve(null);
      });
    });
    
  } catch (error) {
    updateJobStatus(job_id, "failed", 0, `Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};
    
    updateJobStatus(job_id, "processing", 40, "Creating professional voiceovers...");
    
    // Step 2: Generate Audio for each segment
    const audioFiles = [];
    const voiceMap = {
      professional: "nova",
      casual: "alloy", 
      energetic: "shimmer",
      friendly: "echo"
    };
    const selectedVoice = voiceMap[tone] || "nova";
    
    for (let i = 0; i < planData.script_segments.length; i++) {
      const segment = planData.script_segments[i];
      const audioFile = path.join(process.cwd(), "static", `audio_${job_id}_${i}.mp3`);
      
      try {
        const ttsResponse = await openai.audio.speech.create({
          model: "tts-1-hd",
          voice: selectedVoice,
          input: segment.voiceover,
          speed: 1.0
        });
        
        const buffer = Buffer.from(await ttsResponse.arrayBuffer());
        fs.writeFileSync(audioFile, buffer);
        audioFiles.push(audioFile);
        
        updateJobStatus(job_id, "processing", 40 + (i + 1) * 4, `Generated voiceover ${i + 1}/5...`);
      } catch (error) {
        console.log(`Audio generation failed for segment ${i}:`, error);
      }
    }
    
    updateJobStatus(job_id, "processing", 70, "Assembling video with synchronized audio...");
    
    // Step 3: Create Video with Audio
    const outputFile = path.join(process.cwd(), "static", `video_${job_id}.mp4`);
    const colors = planData.technical_specs.colors || ['#4A90E2', '#7B68EE', '#FF6B6B', '#50C878', '#FFD700'];
    
    // Build FFmpeg command with audio
    let ffmpegArgs = ['-y'];
    
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
      return `[${i}]drawtext=text='${text}':fontsize=40:fontcolor=white:x=(w-text_w)/2:y=960[v${i}]`;
    }).join(';');
    
    // Concatenate videos
    const videoInputs = planData.script_segments.map((_, i) => `[v${i}]`).join('');
    const videoConcat = `${videoInputs}concat=n=${planData.script_segments.length}:v=1:a=0[video]`;
    
    // Mix audio
    const audioInputStart = planData.script_segments.length;
    const audioMix = audioFiles.length > 0 ? 
      `;${audioFiles.map((_, i) => `[${audioInputStart + i}]`).join('')}concat=n=${audioFiles.length}:v=0:a=1[audio]` : '';
    
    const filterComplex = videoFilters + ';' + videoConcat + audioMix;
    
    ffmpegArgs.push('-filter_complex', filterComplex, '-map', '[video]');
    
    if (audioFiles.length > 0) {
      ffmpegArgs.push('-map', '[audio]');
    }
    
    ffmpegArgs.push('-c:v', 'libx264', '-c:a', 'aac', '-pix_fmt', 'yuv420p', '-r', '30', outputFile);
    
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
    
  } catch (error) {
    updateJobStatus(job_id, "failed", 0, `Error: ${error.message}`);
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
      
      // Initialize job status
      updateJobStatus(job_id, "queued", 0, "Video generation queued");
      
      // Start video generation in background with immediate execution
      setImmediate(() => {
        generateVideo(job_id, req.body).catch(error => {
          console.error(`Video generation failed for ${job_id}:`, error);
          updateJobStatus(job_id, "failed", 0, `Error: ${error.message}`);
        });
      });
      
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
