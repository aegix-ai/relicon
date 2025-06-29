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

// Generate synchronized captions from actual audio files
const generateSynchronizedCaptions = async (audioFiles: string[], scriptData: any, job_id: string) => {
  const captionData: any[] = [];
  let currentTime = 0;
  
  for (let i = 0; i < audioFiles.length; i++) {
    const audioFile = audioFiles[i];
    const segment = scriptData.segments[i];
    
    // Get actual audio duration using ffprobe
    const probePath = `/tmp/probe_${job_id}_${i}.py`;
    const probeScript = `
import subprocess
import json

try:
    result = subprocess.run([
        'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', 
        '${audioFile}'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        print(f"DURATION_SUCCESS:{duration}")
    else:
        print("DURATION_ERROR:Could not get duration")
except Exception as e:
    print(f"DURATION_ERROR:{str(e)}")
`;
    
    fs.writeFileSync(probePath, probeScript);
    
    const probe = spawn('python', [probePath], { env: { ...process.env } });
    let probeOutput = '';
    
    await new Promise((resolve) => {
      probe.stdout.on('data', (data) => { probeOutput += data.toString(); });
      probe.on('close', () => {
        fs.unlinkSync(probePath);
        resolve(null);
      });
    });
    
    let actualDuration = segment.duration; // fallback
    if (probeOutput.includes('DURATION_SUCCESS:')) {
      actualDuration = parseFloat(probeOutput.split('DURATION_SUCCESS:')[1]);
    }
    
    // Create caption segments based on actual audio timing
    const enhancedText = segment.text;
    const words = enhancedText.split(' ').filter(w => w.length > 0);
    const wordsPerSecond = words.length / actualDuration;
    const avgWordsPerCaption = Math.max(3, Math.min(6, Math.floor(8 / wordsPerSecond)));
    
    // Split into caption chunks that will appear/disappear naturally
    let wordIndex = 0;
    let captionStartTime = currentTime;
    
    while (wordIndex < words.length) {
      const captionWords = words.slice(wordIndex, wordIndex + avgWordsPerCaption);
      const captionText = captionWords.join(' ');
      const captionDuration = captionWords.length / wordsPerSecond;
      
      captionData.push({
        text: captionText,
        startTime: captionStartTime,
        endTime: captionStartTime + captionDuration,
        segmentIndex: i,
        energy: segment.energy
      });
      
      wordIndex += avgWordsPerCaption;
      captionStartTime += captionDuration;
    }
    
    currentTime += actualDuration;
  }
  
  console.log('Generated synchronized captions:', captionData.length, 'caption segments');
  return captionData;
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

Create script with natural, conversational speech that feels human and energetic:

CRITICAL AUDIO REQUIREMENTS:
- Write like you're speaking to a friend - natural, conversational tone
- Use questions to engage ("Have you ever felt...?", "What if I told you...?")
- Add emotional expressions ("Wow!", "Listen...", "Here's the thing...")
- Include natural pauses and rhythm breaks
- Build energy progressively through each scene
- Make it feel like a real person talking, not robotic text
- Each segment should feel complete but connected to the story arc

PACING GUIDELINES:
- Hook: Start with energy, grab attention immediately
- Problem: Build tension with relatable pain points  
- Solution: Reveal with excitement and clarity
- Proof: Speak with confidence and authority
- CTA: Create urgency but don't rush

Write conversational, human dialogue that will sound natural when spoken aloud.

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
import requests
import json

# ElevenLabs API configuration
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
ELEVENLABS_URL = "https://api.elevenlabs.io/v1/text-to-speech"

# CONSISTENT VOICE SYSTEM - Max 2 voices, default to 1
# Primary voice for most content - natural and engaging
PRIMARY_VOICE = "TX3LPaxmHKxFdv7VOQHJ"  # Liam - versatile, natural
# Secondary voice only for contrast when needed
SECONDARY_VOICE = "pNInz6obpgDQGcFmaJgB"  # Adam - professional depth

# Use primary voice for most segments, secondary only for authority/proof
voice_map = {
    "explosive": PRIMARY_VOICE,    # Hook - engaging and energetic
    "tension": PRIMARY_VOICE,      # Problem - same voice for continuity
    "exciting": PRIMARY_VOICE,     # Solution - maintain connection
    "confident": SECONDARY_VOICE,  # Proof - add authority when needed
    "urgent": PRIMARY_VOICE        # CTA - back to primary for action
}

segment_energy = "${segment.energy}"
voice_id = voice_map.get(segment_energy, "TX3LPaxmHKxFdv7VOQHJ")

# ENHANCED TEXT with natural pacing and energy
original_text = """${segment.text}"""
target_duration = ${segment.duration}

# Add natural speech patterns based on energy and duration
if segment_energy == "explosive":
    # Hook - punchy, attention-grabbing
    enhanced_text = f"Hey! {original_text}... Think about that."
elif segment_energy == "tension": 
    # Problem - build suspense with pauses
    enhanced_text = f"Here's the truth... {original_text}. And that's frustrating, right?"
elif segment_energy == "exciting":
    # Solution - enthusiastic reveal
    enhanced_text = f"But here's what changes everything: {original_text}! This is exactly what you need."
elif segment_energy == "confident":
    # Proof - authoritative and trustworthy  
    enhanced_text = f"The results speak for themselves. {original_text}. That's the difference."
else:
    # CTA - urgent but not rushed
    enhanced_text = f"So here's what you do next: {original_text}. Don't wait on this."

# Add strategic pauses for pacing (based on target duration)
if target_duration >= 5.0:
    enhanced_text = enhanced_text.replace(". ", "... ").replace("! ", "! ... ").replace("? ", "? ... ")

print(f"ENHANCED_TEXT: {enhanced_text}")

try:
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    # Professional voice settings for natural, engaging speech
    data = {
        "text": enhanced_text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.75,        # Stable but natural
            "similarity_boost": 0.85, # Clear voice character
            "style": 0.8,            # Expressive delivery
            "use_speaker_boost": True # Enhanced clarity
        }
    }
    
    response = requests.post(f"{ELEVENLABS_URL}/{voice_id}", json=data, headers=headers)
    
    if response.status_code == 200:
        with open("${audioFile}", "wb") as f:
            f.write(response.content)
        print("AUDIO_SUCCESS:${audioFile}")
    else:
        print(f"ELEVENLABS_ERROR: {response.status_code} - {response.text}")
        
        # Fallback to OpenAI if ElevenLabs fails
        from openai import OpenAI
        openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        fallback_response = openai.audio.speech.create(
            model="tts-1-hd",
            voice="nova",
            input=enhanced_text,
            speed=0.9  # Slightly slower for better pacing
        )
        fallback_response.stream_to_file("${audioFile}")
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
        
        updateJobStatus(job_id, "processing", 80, "Creating synchronized captions...");
        
        // REVOLUTIONARY: Generate captions from actual audio duration and timing
        const captionData = await generateSynchronizedCaptions(audioFiles, scriptData, job_id);
        
        updateJobStatus(job_id, "processing", 85, "Assembling final video with synced captions...");
        
        // Create video with synchronized captions
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
        
        // SYNCHRONIZED CAPTION BACKGROUNDS - Scene changes on audio pauses
        const totalDuration = Math.ceil(captionData[captionData.length - 1]?.endTime || duration);
        
        // Generate background scenes that change with natural pauses in speech
        let currentTime = 0;
        let sceneIndex = 0;
        
        for (let i = 0; i < scriptData.segments.length; i++) {
          const segment = scriptData.segments[i];
          const colors = energyColors[segment.energy] || energyColors.exciting;
          const color = colors[sceneIndex % colors.length];
          
          // Create scene for this segment duration  
          ffmpegArgs.push('-f', 'lavfi', '-i', `color=c=${color}:size=1080x1920:duration=${segment.duration}`);
          sceneIndex++;
        }
        
        // Add audio inputs
        audioFiles.forEach((file: string) => {
          if (fs.existsSync(file)) {
            ffmpegArgs.push('-i', file);
          }
        });
        
        // CLEAN SYNCHRONIZED CAPTION SYSTEM - Match actual audio timing
        // Create base video filters with background colors per segment
        const baseVideoFilters = scriptData.segments.map((segment: any, i: number) => {
          return `[${i}]copy[v${i}]`;
        }).join(';');
        
        // Generate synchronized captions that appear/disappear with speech timing
        const captionFilters = captionData.map((caption: any, i: number) => {
          let text = caption.text
            .replace(/['"\\`]/g, '')
            .replace(/[^\w\s!?.,-]/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
          
          if (!text || text.length === 0) text = 'Ready';
          
          // Smart font sizing for readability
          const fontSize = Math.max(52, Math.min(78, Math.floor(1000 / text.length)));
          
          // Energy-based caption colors
          const energyColors = {
            explosive: '0xFF1744@0.9',
            tension: '0x1C1C1E@0.9', 
            exciting: '0x007AFF@0.85',
            confident: '0x34C759@0.9',
            urgent: '0xAD1457@0.9'
          };
          
          const bgColor = energyColors[caption.energy as keyof typeof energyColors] || energyColors.exciting;
          
          // Create synchronized caption with timing controls
          const startTime = caption.startTime;
          const endTime = caption.endTime;
          
          // Return synchronized caption filter
          return `drawtext=text='${text}':fontsize=${fontSize}:fontcolor=white:x=(w-text_w)/2:y=1200:box=1:boxcolor=${bgColor}:boxborderw=8:enable='between(t,${startTime},${endTime})'`;
        }).join(':');
        
        // SIMPLIFIED SYNCHRONIZED CAPTION SYSTEM
        // Create transitions first, then add synchronized captions to final video
        let transitionChain = '';
        
        if (scriptData.segments.length === 1) {
          transitionChain = `[v0]copy[background]`;
        } else {
          // Multi-segment transitions that change on audio pauses
          let currentInput = `[v0]`;
          let runningTime = 0;
          
          for (let i = 1; i < scriptData.segments.length; i++) {
            runningTime += scriptData.segments[i-1].duration;
            const transitionDuration = 0.3;
            const offset = Math.max(0.1, runningTime - transitionDuration);
            
            if (i === scriptData.segments.length - 1) {
              transitionChain = `${currentInput}[v${i}]xfade=transition=fade:duration=${transitionDuration}:offset=${offset}[background]`;
            } else {
              transitionChain += `${currentInput}[v${i}]xfade=transition=fade:duration=${transitionDuration}:offset=${offset}[t${i}];`;
              currentInput = `[t${i}]`;
            }
          }
        }
        
        // Add synchronized captions to the final background video
        const finalVideo = `[background]${captionFilters}[video]`;
        
        // Add audio mixing
        const audioMix = audioFiles.length > 0 ? 
          `;${audioFiles.map((_, i) => `[${scriptData.segments.length + i}:a]`).join('')}concat=n=${audioFiles.length}:v=0:a=1[audio]` : '';
        
        const filterComplex = baseVideoFilters + ';' + transitionChain + ';' + finalVideo + audioMix;
        
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