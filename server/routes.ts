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
          let audioError = '';
          
          audio.stdout.on('data', (data) => { audioOutput += data.toString(); });
          audio.stderr.on('data', (data) => { audioError += data.toString(); });
          
          await new Promise((audioResolve) => {
            const timeout = setTimeout(() => {
              audio.kill();
              console.log(`Audio generation timeout for segment ${i}`);
              audioResolve(null);
            }, 15000); // 15 second timeout
            
            audio.on('close', (code) => {
              clearTimeout(timeout);
              fs.unlinkSync(audioPath);
              
              if (audioOutput.includes('AUDIO_SUCCESS:')) {
                audioFiles.push(audioFile);
                console.log(`Audio generated successfully for segment ${i}`);
              } else {
                console.log(`Audio generation failed for segment ${i}:`, audioError || audioOutput);
              }
              
              // Update progress after each audio segment
              updateJobStatus(job_id, "processing", 50 + ((i + 1) * 5), `Voiceover ${i + 1}/${scriptData.segments.length} complete`);
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
        
        // Build PROFESSIONAL visual system with intelligent design
        const videoFilters = scriptData.segments.map((segment: any, i: number) => {
          const rawText = segment.text.replace(/['"\\]/g, '').replace(/:/g, ' ');
          const words = rawText.split(' ');
          
          // Intelligent text wrapping - max 32 chars per line, 2 lines max
          const maxCharsPerLine = 32;
          let lines: string[] = [];
          let currentLine = '';
          
          for (const word of words) {
            if (currentLine.length + word.length + 1 <= maxCharsPerLine) {
              currentLine += (currentLine ? ' ' : '') + word;
            } else {
              if (currentLine) lines.push(currentLine);
              currentLine = word;
              if (lines.length >= 2) break; // Max 2 lines
            }
          }
          if (currentLine && lines.length < 2) lines.push(currentLine);
          
          // If still too long, truncate intelligently
          if (lines.length === 0) lines = [rawText.substring(0, maxCharsPerLine)];
          
          // Professional color schemes with FFmpeg-compatible colors
          const colorSchemes: Record<string, {primary: string, secondary: string, accent: string, bg: string}> = {
            explosive: {primary: 'white', secondary: 'yellow', accent: 'red', bg: '0xFF1744@0.85'},
            tension: {primary: 'lightgray', secondary: 'orange', accent: 'gray', bg: '0x37474F@0.9'},
            exciting: {primary: 'white', secondary: 'cyan', accent: 'blue', bg: '0x1A237E@0.8'},
            confident: {primary: 'white', secondary: 'green', accent: 'darkgreen', bg: '0x1B5E20@0.85'},
            urgent: {primary: 'white', secondary: 'orangered', accent: 'magenta', bg: '0xAD1457@0.9'}
          };
          
          const scheme = colorSchemes[segment.energy] || colorSchemes.exciting;
          const fontSize = Math.max(45, Math.min(75, Math.floor(1200 / Math.max(lines[0]?.length || 1, 1))));
          
          // Create sophisticated effects based on visual style
          let textEffect = '';
          const padding = 80; // Safe padding from edges
          const lineHeight = fontSize + 15;
          const startY = lines.length === 1 ? 960 : 900;
          
          switch (segment.visual_style) {
            case 'zoom_burst':
              // Cinematic zoom with fade-in
              if (lines.length === 1) {
                textEffect = `[${i}]drawtext=text='${lines[0]}':fontsize=${fontSize*0.6}:fontcolor=${scheme.primary}:x=(w-text_w)/2:y=${startY}:alpha='t/${segment.duration/3}':box=1:boxcolor=${scheme.bg}:boxborderw=8[v${i}a];[v${i}a]drawtext=text='${lines[0]}':fontsize=${fontSize}:fontcolor=${scheme.secondary}:x=(w-text_w)/2:y=${startY-50}:enable='gte(t,${segment.duration/3})':box=1:boxcolor=${scheme.bg}:boxborderw=12:shadowcolor=${scheme.accent}:shadowx=4:shadowy=4[v${i}]`;
              } else {
                textEffect = `[${i}]drawtext=text='${lines[0]}':fontsize=${fontSize}:fontcolor=${scheme.primary}:x=(w-text_w)/2:y=${startY}:alpha='t/${segment.duration/3}':box=1:boxcolor=${scheme.bg}:boxborderw=8[v${i}a];[v${i}a]drawtext=text='${lines[1]}':fontsize=${fontSize-8}:fontcolor=${scheme.secondary}:x=(w-text_w)/2:y=${startY+lineHeight}:enable='gte(t,${segment.duration/4})':box=1:boxcolor=${scheme.bg}:boxborderw=8[v${i}]`;
              }
              break;
              
            case 'shake_reveal':
              // Dramatic reveal with controlled shake
              if (lines.length === 1) {
                textEffect = `[${i}]drawtext=text='${lines[0]}':fontsize=${fontSize}:fontcolor=${scheme.primary}:x='(w-text_w)/2+3*sin(t*15)':y='${startY}+2*cos(t*18)':box=1:boxcolor=${scheme.bg}:boxborderw=10:shadowcolor=${scheme.accent}:shadowx=3:shadowy=3[v${i}]`;
              } else {
                textEffect = `[${i}]drawtext=text='${lines[0]}':fontsize=${fontSize}:fontcolor=${scheme.primary}:x='(w-text_w)/2+3*sin(t*15)':y='${startY}+2*cos(t*18)':box=1:boxcolor=${scheme.bg}:boxborderw=8[v${i}a];[v${i}a]drawtext=text='${lines[1]}':fontsize=${fontSize-8}:fontcolor=${scheme.secondary}:x='(w-text_w)/2+2*sin(t*12)':y='${startY+lineHeight}+1*cos(t*20)':enable='gte(t,${segment.duration/3})':box=1:boxcolor=${scheme.bg}:boxborderw=6[v${i}]`;
              }
              break;
              
            case 'slide_dynamic':
              // Professional slide-in with stagger
              if (lines.length === 1) {
                textEffect = `[${i}]drawtext=text='${lines[0]}':fontsize=${fontSize}:fontcolor=${scheme.primary}:x='(w-text_w)/2+(w-text_w)*max(0,1-4*t/${segment.duration})':y=${startY}:box=1:boxcolor=${scheme.bg}:boxborderw=10:shadowcolor=${scheme.accent}:shadowx=2:shadowy=2[v${i}]`;
              } else {
                textEffect = `[${i}]drawtext=text='${lines[0]}':fontsize=${fontSize}:fontcolor=${scheme.primary}:x='(w-text_w)/2+(w-text_w)*max(0,1-6*t/${segment.duration})':y=${startY}:box=1:boxcolor=${scheme.bg}:boxborderw=8[v${i}a];[v${i}a]drawtext=text='${lines[1]}':fontsize=${fontSize-8}:fontcolor=${scheme.secondary}:x='(w-text_w)/2-(w-text_w)*max(0,1-6*(t-${segment.duration/5})/${segment.duration})':y=${startY+lineHeight}:enable='gte(t,${segment.duration/5})':box=1:boxcolor=${scheme.bg}:boxborderw=8[v${i}]`;
              }
              break;
              
            case 'fade_glow':
              // Elegant fade with glow effect
              const glowIntensity = 'if(lt(t,0.5),t*2,if(lt(t,1.5),1,2-t))';
              if (lines.length === 1) {
                textEffect = `[${i}]drawtext=text='${lines[0]}':fontsize=${fontSize}:fontcolor=${scheme.primary}:x=(w-text_w)/2:y=${startY}:alpha='${glowIntensity}':box=1:boxcolor=${scheme.bg}:boxborderw=12:shadowcolor=${scheme.secondary}:shadowx=0:shadowy=0:shadowblur=8[v${i}]`;
              } else {
                textEffect = `[${i}]drawtext=text='${lines[0]}':fontsize=${fontSize}:fontcolor=${scheme.primary}:x=(w-text_w)/2:y=${startY}:alpha='${glowIntensity}':box=1:boxcolor=${scheme.bg}:boxborderw=10[v${i}a];[v${i}a]drawtext=text='${lines[1]}':fontsize=${fontSize-8}:fontcolor=${scheme.secondary}:x=(w-text_w)/2:y=${startY+lineHeight}:alpha='${glowIntensity}':enable='gte(t,${segment.duration/4})':box=1:boxcolor=${scheme.bg}:boxborderw=8[v${i}]`;
              }
              break;
              
            case 'pulse_scale':
              // Rhythmic pulse effect with working color animation
              const pulseScale = `${fontSize}+${Math.floor(fontSize*0.15)}*sin(t*6)`;
              // Use color_expr instead of fontcolor for dynamic colors
              if (lines.length === 1) {
                textEffect = `[${i}]drawtext=text='${lines[0]}':fontsize='${pulseScale}':fontcolor=white:x=(w-text_w)/2:y=${startY}:box=1:boxcolor=${scheme.bg}:boxborderw=10:shadowcolor=${scheme.accent}:shadowx=2:shadowy=2[v${i}]`;
              } else {
                textEffect = `[${i}]drawtext=text='${lines[0]}':fontsize='${pulseScale}':fontcolor=white:x=(w-text_w)/2:y=${startY}:box=1:boxcolor=${scheme.bg}:boxborderw=8[v${i}a];[v${i}a]drawtext=text='${lines[1]}':fontsize=${fontSize-8}:fontcolor=${scheme.secondary}:x=(w-text_w)/2:y=${startY+lineHeight}:enable='gte(t,${segment.duration/4})':box=1:boxcolor=${scheme.bg}:boxborderw=6[v${i}]`;
              }
              break;
              
            default:
              // Professional default with proper padding
              if (lines.length === 1) {
                textEffect = `[${i}]drawtext=text='${lines[0]}':fontsize=${fontSize}:fontcolor=${scheme.primary}:x=(w-text_w)/2:y=${startY}:box=1:boxcolor=${scheme.bg}:boxborderw=10[v${i}]`;
              } else {
                textEffect = `[${i}]drawtext=text='${lines[0]}':fontsize=${fontSize}:fontcolor=${scheme.primary}:x=(w-text_w)/2:y=${startY}:box=1:boxcolor=${scheme.bg}:boxborderw=8[v${i}a];[v${i}a]drawtext=text='${lines[1]}':fontsize=${fontSize-8}:fontcolor=${scheme.secondary}:x=(w-text_w)/2:y=${startY+lineHeight}:box=1:boxcolor=${scheme.bg}:boxborderw=6[v${i}]`;
              }
          }
          
          return textEffect;
        }).join(';');
        
        // Intelligent transitions based on segment energy flow
        let transitionChain = '';
        
        if (scriptData.segments.length === 1) {
          transitionChain = `[v0]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black[video]`;
        } else {
          // Create intelligent transitions based on energy flow
          const transitions: Record<string, string> = {
            'explosive_to_tension': 'fadeblack',
            'explosive_to_exciting': 'dissolve', 
            'tension_to_exciting': 'wiperight',
            'tension_to_confident': 'slideup',
            'exciting_to_confident': 'fade',
            'exciting_to_urgent': 'dissolve',
            'confident_to_urgent': 'wipeleft',
            'any_to_any': 'crossfade'
          };
          
          let currentInput = `[v0]`;
          
          for (let i = 1; i < scriptData.segments.length; i++) {
            const prevEnergy = scriptData.segments[i-1].energy;
            const currentEnergy = scriptData.segments[i].energy;
            const transitionKey = `${prevEnergy}_to_${currentEnergy}`;
            const transition = transitions[transitionKey] || transitions['any_to_any'];
            
            // Calculate timing for smooth transitions
            const prevDuration = scriptData.segments.slice(0, i).reduce((sum: number, seg: any) => sum + seg.duration, 0);
            const transitionDuration = 0.3;
            const offset = Math.max(0, prevDuration - transitionDuration);
            
            if (i === scriptData.segments.length - 1) {
              // Final transition
              transitionChain += `${currentInput}[v${i}]xfade=transition=${transition}:duration=${transitionDuration}:offset=${offset}[video]`;
            } else {
              // Intermediate transition
              transitionChain += `${currentInput}[v${i}]xfade=transition=${transition}:duration=${transitionDuration}:offset=${offset}[t${i}];`;
              currentInput = `[t${i}]`;
            }
          }
        }
        
        // Add audio mixing
        const audioMix = audioFiles.length > 0 ? 
          `;${audioFiles.map((_, i) => `[${scriptData.segments.length + i}]`).join('')}concat=n=${audioFiles.length}:v=0:a=1[audio]` : '';
        
        const filterComplex = videoFilters + ';' + transitionChain + audioMix;
        
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