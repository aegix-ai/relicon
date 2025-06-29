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

// Simplified AI video generation that actually works
const generateVideo = async (job_id: string, request_data: any) => {
  try {
    const { brand_name, brand_description, tone } = request_data;
    
    updateJobStatus(job_id, "processing", 20, "Creating AI script...");
    
    // Generate script using Python
    const script = `
import os
import json
from openai import OpenAI

openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

brand = "${brand_name}"
desc = "${brand_description}"

prompt = f"""Create an ENERGETIC viral video script for {brand}: {desc}

Make 5 dynamic segments with VARIED durations and extraordinary scenes:
- Hook: 2-3 seconds (instant attention grab)
- Problem: 4-6 seconds (build tension)
- Solution: 8-10 seconds (reveal value)
- Proof: 3-5 seconds (quick validation)  
- CTA: 4-6 seconds (urgent action)

Return JSON: {{'segments': [{{'text': 'COMPELLING hook text', 'duration': 3, 'energy': 'explosive', 'visual_style': 'zoom_burst'}}, {{'text': 'Problem description', 'duration': 5, 'energy': 'tension', 'visual_style': 'shake_reveal'}}, {{'text': 'Solution explanation', 'duration': 9, 'energy': 'exciting', 'visual_style': 'slide_dynamic'}}, {{'text': 'Social proof', 'duration': 4, 'energy': 'confident', 'visual_style': 'fade_glow'}}, {{'text': 'Strong CTA', 'duration': 5, 'energy': 'urgent', 'visual_style': 'pulse_scale'}}]}}"""

try:
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    result = json.loads(response.choices[0].message.content)
    print("SCRIPT_SUCCESS:" + json.dumps(result))
except Exception as e:
    print("SCRIPT_ERROR:" + str(e))
`;

    const scriptPath = `/tmp/script_${job_id}.py`;
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
        
        updateJobStatus(job_id, "processing", 50, "Generating voiceovers...");
        
        // Generate audio for each segment
        const audioFiles: string[] = [];
        const voiceMap: Record<string, string> = {
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
          
          audio.stdout.on('data', (data) => { audioOutput += data.toString(); });
          
          await new Promise((audioResolve) => {
            audio.on('close', () => {
              fs.unlinkSync(audioPath);
              if (audioOutput.includes('AUDIO_SUCCESS:')) {
                audioFiles.push(audioFile);
              }
              audioResolve(null);
            });
          });
        }
        
        updateJobStatus(job_id, "processing", 80, "Assembling final video...");
        
        // Create DYNAMIC video with extensive effects
        const outputFile = path.join(process.cwd(), "static", `video_${job_id}.mp4`);
        
        // Dynamic color palettes based on energy
        const energyColors: Record<string, string[]> = {
          explosive: ['0xFF3B30', '0xFF9500', '0xFFCC00'],
          tension: ['0x8E8E93', '0x48484A', '0x1C1C1E'],
          exciting: ['0x007AFF', '0x5856D6', '0xAF52DE'],
          confident: ['0x34C759', '0x00C7BE', '0x30D158'],
          urgent: ['0xFF2D92', '0xFF6B35', '0xFFD60A']
        };
        
        let ffmpegArgs = ['-y'];
        
        // Add video inputs with varied colors
        scriptData.segments.forEach((segment: any, i: number) => {
          const colors = energyColors[segment.energy] || energyColors.exciting;
          const color = colors[i % colors.length];
          ffmpegArgs.push('-f', 'lavfi', '-i', `color=c=${color}:size=1080x1920:duration=${segment.duration}`);
        });
        
        // Add audio inputs
        audioFiles.forEach((file: string) => {
          if (fs.existsSync(file)) {
            ffmpegArgs.push('-i', file);
          }
        });
        
        // Build DYNAMIC video filters with effects
        const videoFilters = scriptData.segments.map((segment: any, i: number) => {
          const text = segment.text.replace(/['"\\]/g, '').replace(/:/g, ' ');
          const words = text.split(' ');
          
          // Dynamic text sizing based on energy and duration
          const textSizes: Record<string, number> = {
            explosive: 80, tension: 60, exciting: 70, confident: 65, urgent: 75
          };
          const fontSize = textSizes[segment.energy] || 60;
          
          // Dynamic text positions and wrapping
          const maxWidth = 900;
          const lineHeight = fontSize * 1.2;
          
          let textEffect = '';
          
          // Create text wrapping and positioning based on visual style
          switch (segment.visual_style) {
            case 'zoom_burst':
              textEffect = `[${i}]drawtext=text='${text}':fontsize=${fontSize}:fontcolor=white:x=(w-text_w)/2:y=500:enable='between(t,0,${segment.duration/3})':box=1:boxcolor=0x000000@0.5,drawtext=text='${text}':fontsize=${fontSize*1.5}:fontcolor=yellow:x=(w-text_w)/2:y=500:enable='between(t,${segment.duration/3},${segment.duration})':shadow=1:shadowcolor=black:shadowx=3:shadowy=3[v${i}]`;
              break;
              
            case 'shake_reveal':
              textEffect = `[${i}]drawtext=text='${text}':fontsize=${fontSize}:fontcolor=white:x='(w-text_w)/2+10*sin(t*20)':y='960+5*cos(t*30)':box=1:boxcolor=0xFF0000@0.3:enable='between(t,0,${segment.duration})'[v${i}]`;
              break;
              
            case 'slide_dynamic':
              const line1 = words.slice(0, Math.ceil(words.length/2)).join(' ');
              const line2 = words.slice(Math.ceil(words.length/2)).join(' ');
              textEffect = `[${i}]drawtext=text='${line1}':fontsize=${fontSize}:fontcolor=white:x='(w-text_w)/2':y=400:enable='between(t,0,${segment.duration})':box=1:boxcolor=0x0000FF@0.4,drawtext=text='${line2}':fontsize=${fontSize-10}:fontcolor=cyan:x='(w-text_w)/2':y=600:enable='between(t,${segment.duration/4},${segment.duration})':shadow=1:shadowcolor=blue[v${i}]`;
              break;
              
            case 'fade_glow':
              textEffect = `[${i}]drawtext=text='${text}':fontsize=${fontSize}:fontcolor=white:x=(w-text_w)/2:y=960:alpha='if(lt(t,${segment.duration/3}),t*3/${segment.duration},if(lt(t,${segment.duration*2/3}),1,3-3*t/${segment.duration}))':box=1:boxcolor=0x00FF00@0.6[v${i}]`;
              break;
              
            case 'pulse_scale':
              textEffect = `[${i}]drawtext=text='${text}':fontsize='${fontSize}+20*sin(t*8)':fontcolor='if(lt(mod(t,0.5),0.25),white,red)':x=(w-text_w)/2:y=960:enable='between(t,0,${segment.duration})':box=1:boxcolor=0xFFFF00@0.5[v${i}]`;
              break;
              
            default:
              textEffect = `[${i}]drawtext=text='${text}':fontsize=${fontSize}:fontcolor=white:x=(w-text_w)/2:y=960[v${i}]`;
          }
          
          return textEffect;
        }).join(';');
        
        // Add transition effects between segments
        const transitionEffects = [];
        for (let i = 0; i < scriptData.segments.length - 1; i++) {
          const currentEnd = scriptData.segments.slice(0, i + 1).reduce((sum: number, seg: any) => sum + seg.duration, 0);
          const transitionDuration = 0.5;
          
          // Various transition types
          const transitions = ['fade', 'wipeleft', 'wiperight', 'slidedown', 'slideup', 'dissolve'];
          const transition = transitions[i % transitions.length];
          
          transitionEffects.push(`[v${i}][v${i+1}]xfade=transition=${transition}:duration=${transitionDuration}:offset=${currentEnd - transitionDuration}[t${i}]`);
        }
        
        // Build complete filter chain
        let filterChain = videoFilters;
        
        if (transitionEffects.length > 0) {
          filterChain += ';' + transitionEffects.join(';');
          
          // Final video output
          const lastTransition = transitionEffects.length - 1;
          filterChain += `;[t${lastTransition}]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black[video]`;
        } else {
          // No transitions, just concatenate
          const videoInputs = scriptData.segments.map((_: any, i: number) => `[v${i}]`).join('');
          filterChain += `;${videoInputs}concat=n=${scriptData.segments.length}:v=1:a=0[video]`;
        }
        
        // Add audio mixing
        const audioMix = audioFiles.length > 0 ? 
          `;${audioFiles.map((_, i) => `[${scriptData.segments.length + i}]`).join('')}concat=n=${audioFiles.length}:v=0:a=1[audio]` : '';
        
        const filterComplex = filterChain + audioMix;
        
        ffmpegArgs.push('-filter_complex', filterComplex, '-map', '[video]');
        
        if (audioFiles.length > 0) {
          ffmpegArgs.push('-map', '[audio]');
        }
        
        ffmpegArgs.push('-c:v', 'libx264', '-c:a', 'aac', '-pix_fmt', 'yuv420p', '-r', '30', '-crf', '23', outputFile);
        
        const ffmpeg = spawn('ffmpeg', ffmpegArgs);
        
        ffmpeg.on('close', (code) => {
          // Clean up audio files
          audioFiles.forEach(file => {
            if (fs.existsSync(file)) fs.unlinkSync(file);
          });
          
          if (code === 0 && fs.existsSync(outputFile)) {
            const size = fs.statSync(outputFile).size;
            updateJobStatus(job_id, "completed", 100, `AI video with voiceover created! (${size} bytes)`, {
              video_url: `/static/video_${job_id}.mp4`,
              completed_at: new Date().toISOString()
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
    updateJobStatus(job_id, "failed", 0, `Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
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
      
      // Start video generation in background
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