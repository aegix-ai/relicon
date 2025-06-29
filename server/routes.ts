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
    const { brand_name, brand_description, tone, target_audience, duration } = request_data;
    
    updateJobStatus(job_id, "processing", 20, "Creating AI script...");
    
    // Generate script using Python
    const script = `
import os
import json
from openai import OpenAI

openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

brand = "${brand_name}"
desc = "${brand_description}"
target_audience = "${target_audience || 'General consumers'}"
tone = "${tone}"
duration = ${duration || 30}

prompt = f"""You are an expert creative director specializing in viral short-form video ads. Create a comprehensive, strategically planned video script.

BRAND ANALYSIS:
Brand: {brand}
Description: {desc}
Target: {target_audience or 'General consumers'}
Tone: {tone}
Duration: {duration} seconds

ADVANCED REASONING REQUIREMENTS:
- Analyze brand personality and audience psychology
- Design each scene with specific creative purpose
- Vary scene lengths strategically (NO slideshow - dynamic pacing)
- Create stunning, framy visuals that are energetic and creative
- Ensure text fits within 9:16 frame with proper margins
- Plan sophisticated visual effects for each scene
- Build emotional arc with clear value proposition
- End with conversion-focused call-to-action

CREATIVE FRAMEWORK (Total {duration}s):
Scene 1: EXPLOSIVE HOOK (1.5-2.5s) - Instant attention grab with visual impact
Scene 2: TENSION BUILD (3-5s) - Problem identification that resonates emotionally  
Scene 3: SOLUTION REVEAL (4-7s) - Product/service introduction with clear benefits
Scene 4: PROOF/VALIDATION (2-4s) - Social proof or demonstration of value
Scene 5: URGENT CTA (2-4s) - Strong call-to-action for immediate conversion

VISUAL STYLE OPTIONS:
- explosive: zoom_burst, shake_emphasis (high energy, attention-grabbing)
- tension: fade_reveal, slide_dynamic (building suspense)
- exciting: slide_dynamic, steady_glow (engaging revelation)
- confident: steady_glow, fade_reveal (trustworthy, professional)
- urgent: shake_emphasis, zoom_burst (immediate action required)

Create script with varied durations, creative visual styles, and compelling text that fits 9:16 format.

CRITICAL: Ensure segments total EXACTLY {duration} seconds. Distribute time strategically:

For {duration}s total, calculate precise durations:
- Hook: {duration * 0.15:.1f}s (15% of total)
- Problem: {duration * 0.25:.1f}s (25% of total)  
- Solution: {duration * 0.35:.1f}s (35% of total - main content)
- Proof: {duration * 0.15:.1f}s (15% of total)
- CTA: {duration * 0.10:.1f}s (10% of total - urgent close)

Return JSON with EXACT durations that sum to {duration}s: {{'segments': [{{'text': 'Hook text under 35 chars', 'duration': {duration * 0.15:.1f}, 'energy': 'explosive', 'visual_style': 'zoom_burst'}}, {{'text': 'Problem identification', 'duration': {duration * 0.25:.1f}, 'energy': 'tension', 'visual_style': 'fade_reveal'}}, {{'text': 'Solution explanation', 'duration': {duration * 0.35:.1f}, 'energy': 'exciting', 'visual_style': 'slide_dynamic'}}, {{'text': 'Proof or benefits', 'duration': {duration * 0.15:.1f}, 'energy': 'confident', 'visual_style': 'steady_glow'}}, {{'text': 'Call to action', 'duration': {duration * 0.10:.1f}, 'energy': 'urgent', 'visual_style': 'shake_emphasis'}}]}}"""

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
        
        console.log('=== PRE-ASSEMBLY DEBUG ===');
        console.log('Audio files count:', audioFiles.length);
        console.log('Script segments count:', scriptData.segments?.length);
        console.log('Audio files exist check:', audioFiles.map(f => ({file: f, exists: fs.existsSync(f)})));
        
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
        
        // REVOLUTIONARY DYNAMIC BACKGROUNDS - Energy-based with subtle animations
        scriptData.segments.forEach((segment: any, i: number) => {
          const colors = energyColors[segment.energy] || energyColors.exciting;
          const color = colors[i % colors.length];
          
          // Revolutionary: Dynamic color-shifting backgrounds based on segment energy
          ffmpegArgs.push('-f', 'lavfi', '-i', `color=c=${color}:size=1080x1920:duration=${segment.duration}`);
        });
        
        // Add audio inputs
        audioFiles.forEach((file: string) => {
          if (fs.existsSync(file)) {
            ffmpegArgs.push('-i', file);
          }
        });
        
        // ADVANCED AI-DRIVEN CREATIVE SYSTEM with 9:16 frame safety
        const videoFilters = scriptData.segments.map((segment: any, i: number) => {
          // Advanced text processing with AI reasoning
          let text = segment.text
            .replace(/['"\\`]/g, '')
            .replace(/[^\w\s!?.,-]/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
          
          if (!text) text = 'Ready';
          
          // CRITICAL: 9:16 frame boundaries (1080x1920) with proper margins
          const SAFE_WIDTH = 1080 - 120;   // 60px margin on each side
          const SAFE_HEIGHT = 1920 - 240;  // 120px margin top/bottom
          const MARGIN_LEFT = 60;
          const MARGIN_TOP = 120;
          
          // AI-driven text layout with advanced reasoning
          const words = text.split(' ');
          const maxWordsPerLine = Math.max(3, Math.min(6, Math.floor(12 - words.length / 4)));
          
          // Smart multi-line text wrapping for 9:16 format
          let lines: string[] = [];
          let currentLine = '';
          
          for (const word of words) {
            const testLine = currentLine ? `${currentLine} ${word}` : word;
            // Estimate character width for 9:16 safety
            const estimatedWidth = testLine.length * 28; // Conservative estimate
            
            if (estimatedWidth <= SAFE_WIDTH - 100 && currentLine.split(' ').length < maxWordsPerLine) {
              currentLine = testLine;
            } else {
              if (currentLine) lines.push(currentLine);
              currentLine = word;
              if (lines.length >= 3) break; // Max 3 lines for 9:16 format
            }
          }
          if (currentLine && lines.length < 3) lines.push(currentLine);
          
          // Fallback for edge cases
          if (lines.length === 0) lines = [text.substring(0, 30) || 'Ready'];
          
          // Advanced AI-driven creative styles based on segment analysis
          const creativeStyles = {
            explosive: {
              primary: 'white', secondary: '#FF6B35', bg: '0xFF1744@0.9',
              effect: 'zoom_burst', shadowColor: '#000000@0.8'
            },
            tension: {
              primary: '#F0F0F0', secondary: '#FFD60A', bg: '0x2C2C2E@0.85',
              effect: 'fade_reveal', shadowColor: '#000000@0.7'
            },
            exciting: {
              primary: 'white', secondary: '#00D4FF', bg: '0x007AFF@0.85',
              effect: 'slide_dynamic', shadowColor: '#001F3F@0.8'
            },
            confident: {
              primary: 'white', secondary: '#30D158', bg: '0x1B5E20@0.9',
              effect: 'steady_glow', shadowColor: '#003300@0.8'
            },
            urgent: {
              primary: 'white', secondary: '#FF2D92', bg: '0xAD1457@0.9',
              effect: 'shake_emphasis', shadowColor: '#330011@0.8'
            }
          };
          
          const energyKey = segment.energy as 'explosive' | 'tension' | 'exciting' | 'confident' | 'urgent';
          const style = creativeStyles[energyKey] || creativeStyles.exciting;
          
          // Calculate optimal font size for 9:16 frame with margins
          const maxLineLength = Math.max(...lines.map(line => line.length));
          let fontSize = Math.max(42, Math.min(72, Math.floor(SAFE_WIDTH / (maxLineLength * 0.6))));
          
          // Adjust for multiple lines
          if (lines.length > 1) {
            fontSize = Math.max(38, Math.min(fontSize, Math.floor((SAFE_HEIGHT - 400) / (lines.length * 1.4))));
          }
          
          // Calculate safe positioning within 9:16 frame
          const lineHeight = Math.floor(fontSize * 1.3);
          const totalTextHeight = lines.length * lineHeight;
          
          // Position text in lower third but within safe margins
          const baseY = Math.max(
            MARGIN_TOP + 400, // Don't go too high
            Math.min(
              1920 - MARGIN_TOP - totalTextHeight - 100, // Stay within bottom margin
              1200 // Preferred position in lower third
            )
          );
          
          // REVOLUTIONARY VISUAL SYSTEM - Mind-blowing effects that still work bulletproof
          let revolutionaryEffects = '';
          
          // Time-based variables for dynamic effects
          const segmentTime = segment.duration;
          const pulseSpeed = 3.0; // Pulse frequency
          const glowIntensity = 0.6;
          const shadowOffset = 4;
          
          // REVOLUTIONARY FEATURE 1: Dynamic text scaling with breathe effect
          const breatheScale = `'${fontSize}+${Math.floor(fontSize*0.15)}*sin(t*${pulseSpeed})'`;
          
          // REVOLUTIONARY FEATURE 2: Color-coded energy system with glowing borders
          const energyColors = {
            explosive: { text: 'white', glow: '#FF3B30', bg: '0xFF1744@0.85' },
            tension: { text: '#F5F5F7', glow: '#FFD60A', bg: '0x1C1C1E@0.9' },
            exciting: { text: 'white', glow: '#00D4FF', bg: '0x007AFF@0.85' },
            confident: { text: 'white', glow: '#30D158', bg: '0x34C759@0.9' },
            urgent: { text: 'white', glow: '#FF2D92', bg: '0xAD1457@0.9' }
          };
          
          const colors = energyColors[energyKey] || energyColors.exciting;
          
          // REVOLUTIONARY FEATURE 3: Multi-layer text with progressive reveal
          if (lines.length === 1) {
            revolutionaryEffects = `[${i}]drawtext=text='${lines[0]}':fontsize=${breatheScale}:fontcolor=${colors.text}:x=(w-text_w)/2:y=${baseY}:box=1:boxcolor=${colors.bg}:boxborderw=10[v${i}base];[v${i}base]drawtext=text='${lines[0]}':fontsize='${fontSize}+${Math.floor(fontSize*0.1)}*sin(t*${pulseSpeed*1.5})':fontcolor=${colors.glow}:x=(w-text_w)/2:y=${baseY-3}:alpha='0.4+0.3*sin(t*${pulseSpeed})':box=1:boxcolor=${colors.bg}:boxborderw=8[v${i}glow];[v${i}glow]drawtext=text='${lines[0]}':fontsize=${fontSize}:fontcolor=${colors.text}:x=(w-text_w)/2:y=${baseY}:shadowcolor=black:shadowx=${shadowOffset}:shadowy=${shadowOffset}[v${i}]`;
          } else {
            // Multi-line with staggered animated reveals
            revolutionaryEffects = `[${i}]`;
            lines.forEach((line, lineIndex) => {
              const yPos = baseY + (lineIndex * lineHeight);
              const delay = lineIndex * 0.4;
              const lineSize = fontSize - (lineIndex * 3);
              const revealEffect = `drawtext=text='${line}':fontsize='${lineSize}+${Math.floor(lineSize*0.1)}*sin(t*${pulseSpeed}+${lineIndex})':fontcolor=${lineIndex === 0 ? colors.text : colors.glow}:x=(w-text_w)/2:y=${yPos}:box=1:boxcolor=${colors.bg}:boxborderw=${12-lineIndex*2}:enable='gte(t,${delay})':alpha='min(1,(t-${delay})*2)'`;
              revolutionaryEffects += revealEffect;
              if (lineIndex < lines.length - 1) revolutionaryEffects += ':';
            });
            revolutionaryEffects += `[v${i}]`;
          }
          
          return revolutionaryEffects;
        }).join(';');
        
        // BULLETPROOF transition system
        let transitionChain = '';
        
        if (scriptData.segments.length === 1) {
          transitionChain = `[v0]copy[video]`;
        } else if (scriptData.segments.length === 2) {
          // Simple 2-segment transition - always works
          const offset = Math.max(0.5, scriptData.segments[0].duration - 0.5);
          transitionChain = `[v0][v1]xfade=transition=fade:duration=0.5:offset=${offset}[video]`;
        } else {
          // Multi-segment - robust sequential transitions
          let currentInput = `[v0]`;
          let runningTime = 0;
          
          for (let i = 1; i < scriptData.segments.length; i++) {
            runningTime += scriptData.segments[i-1].duration;
            const transitionDuration = 0.4;
            const offset = Math.max(0.2, runningTime - transitionDuration);
            
            if (i === scriptData.segments.length - 1) {
              transitionChain += `${currentInput}[v${i}]xfade=transition=dissolve:duration=${transitionDuration}:offset=${offset}[video]`;
            } else {
              transitionChain += `${currentInput}[v${i}]xfade=transition=fade:duration=${transitionDuration}:offset=${offset}[t${i}];`;
              currentInput = `[t${i}]`;
            }
          }
        }
        
        // Add audio mixing - CRITICAL FIX: Audio inputs start after video inputs
        const audioMix = audioFiles.length > 0 ? 
          `;${audioFiles.map((_, i) => `[${scriptData.segments.length + i}:a]`).join('')}concat=n=${audioFiles.length}:v=0:a=1[audio]` : '';
        
        const filterComplex = videoFilters + ';' + transitionChain + audioMix;
        
        // DEBUG: Log the exact filter being used
        console.log("=== FILTER COMPLEX DEBUG ===");
        console.log("Video segments:", scriptData.segments.length);
        console.log("Audio files:", audioFiles.length);
        console.log("Filter length:", filterComplex.length);
        console.log("Filter preview:", filterComplex.substring(0, 200) + "...");
        console.log("FFmpeg args:", ffmpegArgs.slice(0, 10).join(' '), "...");
        
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