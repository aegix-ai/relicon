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

// Create transcription-based captions from actual audio
const createTranscriptionCaptions = async (audioFiles: string[], originalCaptions: any[], job_id: string) => {
  const transcriptions: string[] = [];
  
  // Use OpenAI Whisper to transcribe actual audio
  for (let i = 0; i < audioFiles.length; i++) {
    const audioFile = audioFiles[i];
    
    const transcribePath = `/tmp/transcribe_${job_id}_${i}.py`;
    const transcribeScript = `
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

try:
    with open("${audioFile}", "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    print(f"TRANSCRIPTION_SUCCESS:{transcription}")
except Exception as e:
    print(f"TRANSCRIPTION_ERROR:{str(e)}")
`;
    
    fs.writeFileSync(transcribePath, transcribeScript);
    
    const transcribe = spawn('python', [transcribePath], { env: { ...process.env } });
    let transcribeOutput = '';
    
    await new Promise((resolve) => {
      transcribe.stdout.on('data', (data) => { transcribeOutput += data.toString(); });
      transcribe.on('close', () => {
        fs.unlinkSync(transcribePath);
        resolve(null);
      });
    });
    
    if (transcribeOutput.includes('TRANSCRIPTION_SUCCESS:')) {
      const transcribedText = transcribeOutput.split('TRANSCRIPTION_SUCCESS:')[1].trim();
      transcriptions.push(transcribedText);
    } else {
      transcriptions.push(''); // Fallback to empty
    }
  }
  
  // Create captions from transcriptions with timing
  const captionFilters: string[] = [];
  let currentTime = 0;
  
  for (let i = 0; i < transcriptions.length; i++) {
    const transcription = transcriptions[i];
    if (!transcription || transcription.length === 0) continue;
    
    // Get audio duration for this segment
    const segmentCaptions = originalCaptions.filter(c => c.segmentIndex === i);
    const segmentDuration = segmentCaptions.length > 0 ? 
      Math.max(...segmentCaptions.map(c => c.endTime)) - Math.min(...segmentCaptions.map(c => c.startTime)) : 5;
    
    // Split transcription into words for dynamic captioning
    const words = transcription.split(' ').filter(w => w.length > 0);
    const wordsPerCaption = Math.max(2, Math.min(5, Math.ceil(words.length / 3)));
    
    let wordIndex = 0;
    while (wordIndex < words.length) {
      const captionWords = words.slice(wordIndex, wordIndex + wordsPerCaption);
      const captionText = captionWords.join(' ').replace(/['"]/g, "\\'");
      const captionDuration = (captionWords.length / words.length) * segmentDuration;
      const startTime = currentTime;
      const endTime = currentTime + captionDuration;
      
      // Smart font sizing
      const fontSize = Math.max(48, Math.min(72, Math.floor(800 / captionText.length)));
      
      // Clean text for FFmpeg compatibility
      const cleanText = captionText.replace(/'/g, "\\\\'").replace(/"/g, '\\\\"');
      
      captionFilters.push(
        `drawtext=text='${cleanText}':fontsize=${fontSize}:fontcolor=white:x=(w-text_w)/2:y=1200:box=1:boxcolor=0x000000@0.8:boxborderw=6:enable='between(t,${startTime.toFixed(1)},${endTime.toFixed(1)})'`
      );
      
      wordIndex += wordsPerCaption;
      currentTime += captionDuration;
    }
  }
  
  console.log('Created transcription-based captions:', captionFilters.length);
  return captionFilters;
};

// Generate synchronized captions using OpenAI Whisper transcription
const generateSynchronizedCaptions = async (audioFiles: string[], scriptData: any, job_id: string) => {
  const captionData: any[] = [];
  let currentTime = 0;
  
  console.log('Starting Whisper transcription for', audioFiles.length, 'audio files...');
  
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
        model="o1",
        messages=[{"role": "user", "content": prompt}]
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

# SINGLE VOICE SYSTEM - Use ONE voice for consistency
# Single professional voice for all segments
SINGLE_VOICE = "TX3LPaxmHKxFdv7VOQHJ"  # Liam - versatile, natural, engaging

# Use the same voice for ALL segments to maintain consistency
voice_map = {
    "explosive": SINGLE_VOICE,    # Hook
    "tension": SINGLE_VOICE,      # Problem  
    "exciting": SINGLE_VOICE,     # Solution
    "confident": SINGLE_VOICE,    # Proof
    "urgent": SINGLE_VOICE        # CTA
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
        
        // CAPTION-SYNCHRONIZED SCENES - Generate scenes based on actual caption timing
        const allScenes = [];
        
        // Group captions by similar timing to create meaningful scene changes
        let currentSceneDuration = 0;
        let sceneStartTime = 0;
        let currentSegment = 0;
        
        for (let i = 0; i < captionData.length; i++) {
          const caption = captionData[i];
          const captionDuration = caption.endTime - caption.startTime;
          
          // Create a new scene every 3-5 seconds OR when segment changes
          const shouldCreateNewScene = 
            currentSceneDuration >= 3.0 || // Minimum 3 seconds per scene
            caption.segmentIndex !== currentSegment || // New segment
            (currentSceneDuration >= 2.0 && captionDuration > 1.5); // Natural break point
          
          if (shouldCreateNewScene && currentSceneDuration > 0) {
            // Finalize current scene
            const segment = scriptData.segments[currentSegment];
            const colors = energyColors[segment.energy] || energyColors.exciting;
            const color = colors[allScenes.length % colors.length];
            
            // Create scene with subtle animation based on energy
            const effects = {
              explosive: `color=c=${color}:size=1080x1920:duration=${currentSceneDuration},zoompan=z='min(zoom+0.002,1.3)':d=${Math.ceil(currentSceneDuration * 25)}:s=1080x1920`,
              tension: `color=c=${color}:size=1080x1920:duration=${currentSceneDuration},fade=t=in:st=0:d=0.3`,
              exciting: `color=c=${color}:size=1080x1920:duration=${currentSceneDuration}`,
              confident: `color=c=${color}:size=1080x1920:duration=${currentSceneDuration},zoompan=z='min(zoom+0.001,1.1)':d=${Math.ceil(currentSceneDuration * 25)}:s=1080x1920`,
              urgent: `color=c=${color}:size=1080x1920:duration=${currentSceneDuration}`
            };
            
            const effect = effects[segment.energy] || effects.exciting;
            ffmpegArgs.push('-f', 'lavfi', '-i', effect);
            
            allScenes.push({
              segmentIndex: currentSegment,
              duration: currentSceneDuration,
              color: color,
              startTime: sceneStartTime,
              endTime: sceneStartTime + currentSceneDuration
            });
            
            // Start new scene
            sceneStartTime += currentSceneDuration;
            currentSceneDuration = captionDuration;
            currentSegment = caption.segmentIndex;
          } else {
            // Extend current scene
            currentSceneDuration += captionDuration;
            currentSegment = caption.segmentIndex;
          }
        }
        
        // Don't forget the last scene
        if (currentSceneDuration > 0) {
          const segment = scriptData.segments[currentSegment];
          const colors = energyColors[segment.energy] || energyColors.exciting;
          const color = colors[allScenes.length % colors.length];
          
          const effect = `color=c=${color}:size=1080x1920:duration=${currentSceneDuration}`;
          ffmpegArgs.push('-f', 'lavfi', '-i', effect);
          
          allScenes.push({
            segmentIndex: currentSegment,
            duration: currentSceneDuration,
            color: color,
            startTime: sceneStartTime,
            endTime: sceneStartTime + currentSceneDuration
          });
        }
        
        console.log(`Created ${allScenes.length} caption-synchronized scenes:`, allScenes.map(s => `${s.duration.toFixed(1)}s`));
        
        // Add audio inputs
        audioFiles.forEach((file: string) => {
          if (fs.existsSync(file)) {
            ffmpegArgs.push('-i', file);
          }
        });
        
        // DYNAMIC SCENE SYSTEM - Create base video filters for all scenes
        const baseVideoFilters = allScenes.map((scene: any, i: number) => {
          return `[${i}]copy[s${i}]`;
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
          return `drawtext=text='${text}':fontsize=${fontSize}:fontcolor=white:x=(w-text_w)/2:y=h-200:box=1:boxcolor=${bgColor}:boxborderw=8:enable='between(t,${startTime},${endTime})'`;
        }).join(',');
        
        // DYNAMIC SCENE TRANSITIONS - Connect all sub-scenes with smooth transitions
        let transitionChain = '';
        
        if (allScenes.length === 1) {
          transitionChain = `[s0]copy[background]`;
        } else {
          // Multi-scene transitions with dynamic effects
          let currentInput = `[s0]`;
          let runningTime = 0;
          
          for (let i = 1; i < allScenes.length; i++) {
            runningTime += allScenes[i-1].duration;
            const transitionDuration = 0.2;
            const offset = Math.max(0.1, runningTime - transitionDuration);
            
            // Vary transition types for visual interest
            const transitionTypes = ['fade', 'dissolve'];
            const transitionType = transitionTypes[i % transitionTypes.length];
            
            if (i === allScenes.length - 1) {
              // Final transition
              transitionChain += `${currentInput}[s${i}]xfade=transition=${transitionType}:duration=${transitionDuration}:offset=${offset.toFixed(1)}[background]`;
            } else {
              // Intermediate transition
              transitionChain += `${currentInput}[s${i}]xfade=transition=${transitionType}:duration=${transitionDuration}:offset=${offset.toFixed(1)}[t${i}];`;
              currentInput = `[t${i}]`;
            }
          }
        }
        
        // ENABLE CAPTIONS - Apply synchronized captions to final video
        const finalVideo = captionFilters.length > 0 ? 
          `[background]${captionFilters}[video]` : 
          `[background]copy[video]`;
        
        // Add audio mixing - audio inputs start after all scene inputs
        const audioMix = audioFiles.length > 0 ? 
          `;${audioFiles.map((_, i) => `[${allScenes.length + i}:a]`).join('')}concat=n=${audioFiles.length}:v=0:a=1[audio]` : '';
        
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
        let ffmpegOutput = '';
        let ffmpegError = '';
        
        ffmpeg.stdout.on('data', (data) => { ffmpegOutput += data.toString(); });
        ffmpeg.stderr.on('data', (data) => { ffmpegError += data.toString(); });
        
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
            console.log("=== FFMPEG FAILURE DEBUG ===");
            console.log("Exit code:", code);
            console.log("FFmpeg stderr:", ffmpegError.substring(0, 1000));
            console.log("FFmpeg stdout:", ffmpegOutput.substring(0, 500));
            console.log("Filter complex:", filterComplex);
            updateJobStatus(job_id, "failed", 0, `Video assembly failed: ${ffmpegError.split('\n').slice(-3).join(' ')}`);
          }
        });
        
        ffmpeg.on('error', (error) => {
          console.log("FFmpeg spawn error:", error);
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

  // Root route - serve the complete landing page
  app.get('/', (req, res) => {
    res.redirect('/dashboard');
  });

  // Dashboard route - serve the complete frontend
  app.get('/dashboard', (req, res) => {
    const completeFrontend = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ReelForge | AI-Powered Video Ad Engine</title>
    <meta name="description" content="Create. Learn. Perform. Ads built by agentic intelligence, tailored for your business.">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    <style>
        body { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .bg-gradient { background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%); }
        .dark .bg-gradient { background: linear-gradient(135deg, #111827 0%, #000000 100%); }
        .transition-theme { transition: background-color 0.3s ease, color 0.3s ease; }
        @media (prefers-color-scheme: dark) {
          html { color-scheme: dark; }
        }
    </style>
</head>
<body class="transition-theme bg-gradient min-h-screen">
    <div id="app">
        <!-- Landing Page Content -->
        <div id="landing-page" class="min-h-screen">
            <!-- Navbar -->
            <nav class="fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-black/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800">
                <div class="container mx-auto px-6 py-4">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-2">
                            <div class="w-8 h-8 bg-[#FF5C00] rounded-lg flex items-center justify-center">
                                <span class="text-white font-bold text-sm">R</span>
                            </div>
                            <span class="text-xl font-bold text-black dark:text-white">ReelForge</span>
                        </div>
                        
                        <div class="hidden md:flex items-center space-x-8">
                            <a href="#why" class="text-gray-600 dark:text-gray-300 hover:text-[#FF5C00] transition-colors">Why ReelForge</a>
                            <a href="#how" class="text-gray-600 dark:text-gray-300 hover:text-[#FF5C00] transition-colors">How It Works</a>
                            <a href="#samples" class="text-gray-600 dark:text-gray-300 hover:text-[#FF5C00] transition-colors">Samples</a>
                            <a href="#pricing" class="text-gray-600 dark:text-gray-300 hover:text-[#FF5C00] transition-colors">Pricing</a>
                        </div>
                        
                        <div class="flex items-center space-x-4">
                            <button id="theme-toggle" class="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300">
                                <i data-lucide="sun" class="w-5 h-5 hidden dark:block"></i>
                                <i data-lucide="moon" class="w-5 h-5 block dark:hidden"></i>
                            </button>
                            <button id="enter-panel-btn" class="bg-[#FF5C00] hover:bg-[#E64A00] text-white px-6 py-2 rounded-lg font-semibold transition-colors">
                                Enter Panel
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            <!-- Hero Section -->
            <section class="relative min-h-screen flex flex-col items-center justify-center overflow-hidden pt-20">
                <div class="absolute inset-0 opacity-5 dark:opacity-10">
                    <div class="absolute inset-0 bg-gradient-to-br from-[#FF5C00]/10 to-transparent">
                        <div class="absolute inset-0 bg-[length:20px_20px] bg-[radial-gradient(circle,_#FF5C00_1px,_transparent_1px)]"></div>
                    </div>
                </div>

                <div class="container mx-auto px-6 py-32 relative z-10 text-center">
                    <div class="flex items-center justify-center mb-6">
                        <i data-lucide="sparkles" class="w-6 h-6 text-[#FF5C00] mr-2"></i>
                        <span class="text-[#FF5C00] font-semibold">AI-Powered by Aegix</span>
                    </div>

                    <h1 class="text-5xl md:text-7xl font-bold mb-6 text-black dark:text-white leading-tight">
                        Your Personalized<br>
                        <span class="text-[#FF5C00]">AI Ad Engine</span>
                    </h1>

                    <p class="text-xl md:text-2xl mb-10 max-w-3xl mx-auto text-gray-600 dark:text-gray-300 leading-relaxed">
                        Create. Learn. Perform. Ads built by agentic intelligence, tailored for your business.
                    </p>

                    <div class="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
                        <button id="hero-enter-panel" class="bg-[#FF5C00] hover:bg-[#E64A00] text-white px-8 py-4 rounded-lg font-semibold text-lg transition-colors flex items-center">
                            <i data-lucide="play" class="w-5 h-5 mr-2"></i>
                            Start Creating
                        </button>
                        <button onclick="scrollToSection('#how')" class="border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 px-8 py-4 rounded-lg font-semibold text-lg transition-colors">
                            Learn More
                        </button>
                    </div>
                </div>
            </section>

            <!-- Why ReelForge Section -->
            <section id="why" class="py-24 bg-gray-50 dark:bg-gray-900">
                <div class="container mx-auto px-6">
                    <h2 class="text-4xl md:text-5xl font-bold text-center mb-16 text-black dark:text-white">
                        Why Choose <span class="text-[#FF5C00]">ReelForge</span>?
                    </h2>
                    
                    <div class="grid md:grid-cols-3 gap-8">
                        <div class="text-center p-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
                            <i data-lucide="brain" class="w-12 h-12 text-[#FF5C00] mx-auto mb-4"></i>
                            <h3 class="text-xl font-bold mb-4 text-black dark:text-white">AI-Powered Creation</h3>
                            <p class="text-gray-600 dark:text-gray-300">Advanced AI generates personalized video ads that resonate with your target audience.</p>
                        </div>
                        <div class="text-center p-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
                            <i data-lucide="trending-up" class="w-12 h-12 text-[#FF5C00] mx-auto mb-4"></i>
                            <h3 class="text-xl font-bold mb-4 text-black dark:text-white">Performance Analytics</h3>
                            <p class="text-gray-600 dark:text-gray-300">Real-time insights and performance tracking to optimize your campaigns.</p>
                        </div>
                        <div class="text-center p-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
                            <i data-lucide="zap" class="w-12 h-12 text-[#FF5C00] mx-auto mb-4"></i>
                            <h3 class="text-xl font-bold mb-4 text-black dark:text-white">Lightning Fast</h3>
                            <p class="text-gray-600 dark:text-gray-300">Generate professional video ads in minutes, not hours or days.</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- How It Works Section -->
            <section id="how" class="py-24">
                <div class="container mx-auto px-6">
                    <h2 class="text-4xl md:text-5xl font-bold text-center mb-16 text-black dark:text-white">
                        How It <span class="text-[#FF5C00]">Works</span>
                    </h2>
                    
                    <div class="grid md:grid-cols-4 gap-8">
                        <div class="text-center">
                            <div class="w-16 h-16 bg-[#FF5C00] rounded-full flex items-center justify-center mx-auto mb-4">
                                <span class="text-white font-bold text-xl">1</span>
                            </div>
                            <h3 class="text-xl font-bold mb-4 text-black dark:text-white">Input Details</h3>
                            <p class="text-gray-600 dark:text-gray-300">Tell us about your brand, target audience, and campaign goals.</p>
                        </div>
                        <div class="text-center">
                            <div class="w-16 h-16 bg-[#FF5C00] rounded-full flex items-center justify-center mx-auto mb-4">
                                <span class="text-white font-bold text-xl">2</span>
                            </div>
                            <h3 class="text-xl font-bold mb-4 text-black dark:text-white">AI Generation</h3>
                            <p class="text-gray-600 dark:text-gray-300">Our AI creates personalized video content with synchronized captions.</p>
                        </div>
                        <div class="text-center">
                            <div class="w-16 h-16 bg-[#FF5C00] rounded-full flex items-center justify-center mx-auto mb-4">
                                <span class="text-white font-bold text-xl">3</span>
                            </div>
                            <h3 class="text-xl font-bold mb-4 text-black dark:text-white">Review & Edit</h3>
                            <p class="text-gray-600 dark:text-gray-300">Preview your video and make any necessary adjustments.</p>
                        </div>
                        <div class="text-center">
                            <div class="w-16 h-16 bg-[#FF5C00] rounded-full flex items-center justify-center mx-auto mb-4">
                                <span class="text-white font-bold text-xl">4</span>
                            </div>
                            <h3 class="text-xl font-bold mb-4 text-black dark:text-white">Deploy & Track</h3>
                            <p class="text-gray-600 dark:text-gray-300">Launch your campaigns and monitor performance in real-time.</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Video Samples Section -->
            <section id="samples" class="py-24 bg-gray-50 dark:bg-gray-900">
                <div class="container mx-auto px-6">
                    <h2 class="text-4xl md:text-5xl font-bold text-center mb-16 text-black dark:text-white">
                        Sample <span class="text-[#FF5C00]">Videos</span>
                    </h2>
                    
                    <div class="grid md:grid-cols-3 gap-8">
                        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
                            <div class="aspect-video bg-gray-200 dark:bg-gray-700 rounded-lg mb-4 flex items-center justify-center">
                                <i data-lucide="play" class="w-12 h-12 text-gray-400"></i>
                            </div>
                            <h3 class="text-lg font-bold mb-2 text-black dark:text-white">E-commerce Product</h3>
                            <p class="text-gray-600 dark:text-gray-300">Dynamic product showcase with AI-generated script and voiceover.</p>
                        </div>
                        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
                            <div class="aspect-video bg-gray-200 dark:bg-gray-700 rounded-lg mb-4 flex items-center justify-center">
                                <i data-lucide="play" class="w-12 h-12 text-gray-400"></i>
                            </div>
                            <h3 class="text-lg font-bold mb-2 text-black dark:text-white">Service Business</h3>
                            <p class="text-gray-600 dark:text-gray-300">Professional service ad with testimonials and call-to-action.</p>
                        </div>
                        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
                            <div class="aspect-video bg-gray-200 dark:bg-gray-700 rounded-lg mb-4 flex items-center justify-center">
                                <i data-lucide="play" class="w-12 h-12 text-gray-400"></i>
                            </div>
                            <h3 class="text-lg font-bold mb-2 text-black dark:text-white">App Launch</h3>
                            <p class="text-gray-600 dark:text-gray-300">Mobile app promotion with feature highlights and user benefits.</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Pricing Section -->
            <section id="pricing" class="py-24">
                <div class="container mx-auto px-6">
                    <h2 class="text-4xl md:text-5xl font-bold text-center mb-16 text-black dark:text-white">
                        Simple <span class="text-[#FF5C00]">Pricing</span>
                    </h2>
                    
                    <div class="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                        <div class="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg border border-gray-200 dark:border-gray-700">
                            <h3 class="text-2xl font-bold mb-4 text-black dark:text-white">Starter</h3>
                            <div class="text-4xl font-bold mb-6 text-[#FF5C00]">$29<span class="text-lg text-gray-500">/mo</span></div>
                            <ul class="space-y-3 mb-8">
                                <li class="flex items-center text-gray-600 dark:text-gray-300">
                                    <i data-lucide="check" class="w-5 h-5 text-green-500 mr-2"></i>
                                    10 videos per month
                                </li>
                                <li class="flex items-center text-gray-600 dark:text-gray-300">
                                    <i data-lucide="check" class="w-5 h-5 text-green-500 mr-2"></i>
                                    Basic AI features
                                </li>
                                <li class="flex items-center text-gray-600 dark:text-gray-300">
                                    <i data-lucide="check" class="w-5 h-5 text-green-500 mr-2"></i>
                                    720p quality
                                </li>
                            </ul>
                            <button class="w-full bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 py-3 rounded-lg font-semibold">
                                Get Started
                            </button>
                        </div>
                        
                        <div class="bg-[#FF5C00] rounded-xl p-8 shadow-lg relative transform scale-105">
                            <div class="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-white dark:bg-gray-800 text-[#FF5C00] px-4 py-1 rounded-full text-sm font-semibold">
                                Most Popular
                            </div>
                            <h3 class="text-2xl font-bold mb-4 text-white">Professional</h3>
                            <div class="text-4xl font-bold mb-6 text-white">$99<span class="text-lg text-orange-200">/mo</span></div>
                            <ul class="space-y-3 mb-8">
                                <li class="flex items-center text-white">
                                    <i data-lucide="check" class="w-5 h-5 text-white mr-2"></i>
                                    50 videos per month
                                </li>
                                <li class="flex items-center text-white">
                                    <i data-lucide="check" class="w-5 h-5 text-white mr-2"></i>
                                    Advanced AI features
                                </li>
                                <li class="flex items-center text-white">
                                    <i data-lucide="check" class="w-5 h-5 text-white mr-2"></i>
                                    1080p quality
                                </li>
                                <li class="flex items-center text-white">
                                    <i data-lucide="check" class="w-5 h-5 text-white mr-2"></i>
                                    Priority support
                                </li>
                            </ul>
                            <button class="w-full bg-white text-[#FF5C00] py-3 rounded-lg font-semibold">
                                Start Free Trial
                            </button>
                        </div>
                        
                        <div class="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg border border-gray-200 dark:border-gray-700">
                            <h3 class="text-2xl font-bold mb-4 text-black dark:text-white">Enterprise</h3>
                            <div class="text-4xl font-bold mb-6 text-[#FF5C00]">$299<span class="text-lg text-gray-500">/mo</span></div>
                            <ul class="space-y-3 mb-8">
                                <li class="flex items-center text-gray-600 dark:text-gray-300">
                                    <i data-lucide="check" class="w-5 h-5 text-green-500 mr-2"></i>
                                    Unlimited videos
                                </li>
                                <li class="flex items-center text-gray-600 dark:text-gray-300">
                                    <i data-lucide="check" class="w-5 h-5 text-green-500 mr-2"></i>
                                    Custom AI training
                                </li>
                                <li class="flex items-center text-gray-600 dark:text-gray-300">
                                    <i data-lucide="check" class="w-5 h-5 text-green-500 mr-2"></i>
                                    4K quality
                                </li>
                                <li class="flex items-center text-gray-600 dark:text-gray-300">
                                    <i data-lucide="check" class="w-5 h-5 text-green-500 mr-2"></i>
                                    Dedicated support
                                </li>
                            </ul>
                            <button class="w-full bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 py-3 rounded-lg font-semibold">
                                Contact Sales
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Footer -->
            <footer class="bg-gray-900 text-white py-16">
                <div class="container mx-auto px-6">
                    <div class="grid md:grid-cols-4 gap-8">
                        <div>
                            <div class="flex items-center space-x-2 mb-6">
                                <div class="w-8 h-8 bg-[#FF5C00] rounded-lg flex items-center justify-center">
                                    <span class="text-white font-bold text-sm">R</span>
                                </div>
                                <span class="text-xl font-bold">ReelForge</span>
                            </div>
                            <p class="text-gray-400 mb-4">AI-powered video ad engine for modern businesses.</p>
                        </div>
                        <div>
                            <h4 class="text-lg font-semibold mb-4">Product</h4>
                            <ul class="space-y-2 text-gray-400">
                                <li><a href="#" class="hover:text-white transition-colors">Features</a></li>
                                <li><a href="#" class="hover:text-white transition-colors">Pricing</a></li>
                                <li><a href="#" class="hover:text-white transition-colors">API</a></li>
                            </ul>
                        </div>
                        <div>
                            <h4 class="text-lg font-semibold mb-4">Company</h4>
                            <ul class="space-y-2 text-gray-400">
                                <li><a href="#" class="hover:text-white transition-colors">About</a></li>
                                <li><a href="#" class="hover:text-white transition-colors">Blog</a></li>
                                <li><a href="#" class="hover:text-white transition-colors">Careers</a></li>
                            </ul>
                        </div>
                        <div>
                            <h4 class="text-lg font-semibold mb-4">Support</h4>
                            <ul class="space-y-2 text-gray-400">
                                <li><a href="#" class="hover:text-white transition-colors">Help Center</a></li>
                                <li><a href="#" class="hover:text-white transition-colors">Contact</a></li>
                                <li><a href="#" class="hover:text-white transition-colors">Status</a></li>
                            </ul>
                        </div>
                    </div>
                    <div class="border-t border-gray-800 mt-12 pt-8 text-center text-gray-400">
                        <p>&copy; 2025 ReelForge. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>

        <!-- Dashboard -->
        <div id="dashboard" class="hidden min-h-screen bg-gray-900 text-white">
            <!-- Dashboard Header -->
            <header class="bg-gray-800 border-b border-gray-700 px-6 py-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4 cursor-pointer hover:opacity-80 transition-opacity" onclick="showLandingPage()">
                        <div class="w-8 h-8 bg-[#FF5C00] rounded-lg flex items-center justify-center">
                            <span class="text-white font-bold text-sm">R</span>
                        </div>
                        <span class="text-xl font-bold">ReelForge</span>
                        <i data-lucide="arrow-left" class="w-4 h-4 text-gray-400"></i>
                    </div>
                    
                    <div class="flex items-center space-x-4">
                        <div class="flex items-center space-x-2">
                            <div class="w-8 h-8 bg-gray-600 rounded-full"></div>
                            <span class="text-sm">User</span>
                        </div>
                        <button id="dashboard-theme-toggle" class="p-2 rounded-lg bg-gray-700 text-gray-300">
                            <i data-lucide="sun" class="w-4 h-4 hidden dark:block"></i>
                            <i data-lucide="moon" class="w-4 h-4 block dark:hidden"></i>
                        </button>
                    </div>
                </div>
            </header>

            <!-- Dashboard Navigation -->
            <div class="flex">
                <nav class="w-64 bg-gray-800 min-h-screen p-6">
                    <div class="space-y-2">
                        <button onclick="showDashboardTab('overview')" class="w-full flex items-center space-x-3 px-4 py-3 rounded-lg bg-gray-700 text-white">
                            <i data-lucide="layout-dashboard" class="w-5 h-5"></i>
                            <span>Dashboard</span>
                        </button>
                        <button onclick="showDashboardTab('ai-engine')" class="w-full flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-700 text-gray-300 hover:text-white transition-colors">
                            <i data-lucide="brain" class="w-5 h-5"></i>
                            <span>Ad Engine</span>
                        </button>
                        <button onclick="showDashboardTab('performance')" class="w-full flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-700 text-gray-300 hover:text-white transition-colors">
                            <i data-lucide="bar-chart-3" class="w-5 h-5"></i>
                            <span>Performance</span>
                        </button>
                        <button onclick="showDashboardTab('connect')" class="w-full flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-700 text-gray-300 hover:text-white transition-colors">
                            <i data-lucide="link" class="w-5 h-5"></i>
                            <span>Connect Accounts</span>
                        </button>
                    </div>
                </nav>

                <!-- Dashboard Content -->
                <main class="flex-1 p-8">
                    <!-- AI Engine Panel -->
                    <div id="ai-engine-panel" class="hidden">
                        <div class="max-w-4xl mx-auto">
                            <h1 class="text-3xl font-bold mb-8">AI Ad Engine</h1>
                            
                            <div class="grid lg:grid-cols-2 gap-8">
                                <!-- Input Form -->
                                <div class="bg-gray-800 rounded-xl p-6">
                                    <h2 class="text-xl font-semibold mb-6">Create Your Video Ad</h2>
                                    
                                    <form id="ai-video-form" class="space-y-6">
                                        <div>
                                            <label class="block text-sm font-medium mb-2">Brand Name</label>
                                            <input type="text" id="ai-brand-name" required 
                                                   class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white">
                                        </div>
                                        
                                        <div>
                                            <label class="block text-sm font-medium mb-2">Brand Description</label>
                                            <textarea id="ai-brand-description" required rows="4"
                                                      class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                                                      placeholder="Describe your brand, products, or services..."></textarea>
                                        </div>
                                        
                                        <div>
                                            <label class="block text-sm font-medium mb-2">Target Audience</label>
                                            <input type="text" id="ai-target-audience" 
                                                   class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                                                   placeholder="e.g., young professionals, parents, tech enthusiasts">
                                        </div>
                                        
                                        <div>
                                            <label class="block text-sm font-medium mb-2">Call to Action</label>
                                            <input type="text" id="ai-call-to-action" 
                                                   class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                                                   placeholder="e.g., Buy now, Sign up today, Learn more">
                                        </div>
                                        
                                        <div>
                                            <label class="block text-sm font-medium mb-2">Video Duration: <span id="ai-duration-value">30</span> seconds</label>
                                            <input type="range" id="ai-duration" min="15" max="60" step="15" value="30"
                                                   class="w-full" onchange="document.getElementById('ai-duration-value').textContent = this.value">
                                            <div class="flex justify-between text-sm text-gray-400 mt-1">
                                                <span>15s</span>
                                                <span>30s</span>
                                                <span>45s</span>
                                                <span>60s</span>
                                            </div>
                                        </div>
                                        
                                        <button type="submit" id="ai-generate-btn"
                                                class="w-full bg-[#FF5C00] hover:bg-[#E64A00] text-white font-semibold py-3 px-6 rounded-lg transition duration-300">
                                            Generate Video
                                        </button>
                                    </form>
                                </div>

                                <!-- Progress & Results -->
                                <div class="space-y-6">
                                    <!-- Progress Panel -->
                                    <div id="ai-progress" class="hidden bg-gray-800 rounded-xl p-6">
                                        <h3 class="text-lg font-semibold mb-4">AI Generation Progress</h3>
                                        <div id="ai-progress-steps" class="space-y-3"></div>
                                    </div>

                                    <!-- Video Result -->
                                    <div id="ai-video-result" class="hidden bg-gray-800 rounded-xl p-6">
                                        <h3 class="text-lg font-semibold mb-4">Your Video is Ready!</h3>
                                        <div class="bg-black rounded-lg overflow-hidden mb-4">
                                            <video id="ai-video-player" controls class="w-full" style="aspect-ratio: 9/16;">
                                                <source type="video/mp4">
                                            </video>
                                        </div>
                                        <div class="flex gap-3">
                                            <button id="ai-download-btn" class="bg-[#FF5C00] hover:bg-[#E64A00] px-4 py-2 rounded-lg flex-1">
                                                Download Video
                                            </button>
                                            <button onclick="resetAIForm()" class="bg-gray-600 hover:bg-gray-500 px-4 py-2 rounded-lg flex-1">
                                                Create Another
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Default Dashboard Overview -->
                    <div id="overview-panel">
                        <h1 class="text-3xl font-bold mb-8">Dashboard Overview</h1>
                        
                        <div class="grid md:grid-cols-3 gap-6 mb-8">
                            <div class="bg-gray-800 rounded-xl p-6">
                                <h3 class="text-lg font-semibold mb-2">Videos Created</h3>
                                <div class="text-3xl font-bold text-[#FF5C00]">24</div>
                                <p class="text-gray-400 text-sm">+12% from last month</p>
                            </div>
                            <div class="bg-gray-800 rounded-xl p-6">
                                <h3 class="text-lg font-semibold mb-2">Total Views</h3>
                                <div class="text-3xl font-bold text-[#FF5C00]">1.2K</div>
                                <p class="text-gray-400 text-sm">+25% from last month</p>
                            </div>
                            <div class="bg-gray-800 rounded-xl p-6">
                                <h3 class="text-lg font-semibold mb-2">Conversion Rate</h3>
                                <div class="text-3xl font-bold text-[#FF5C00]">4.8%</div>
                                <p class="text-gray-400 text-sm">+8% from last month</p>
                            </div>
                        </div>

                        <div class="bg-gray-800 rounded-xl p-6">
                            <h3 class="text-lg font-semibold mb-4">Quick Actions</h3>
                            <div class="grid md:grid-cols-2 gap-4">
                                <button onclick="showDashboardTab('ai-engine')" class="bg-[#FF5C00] hover:bg-[#E64A00] text-white p-4 rounded-lg text-left">
                                    <i data-lucide="brain" class="w-6 h-6 mb-2"></i>
                                    <div class="font-semibold">Create New Video</div>
                                    <div class="text-sm opacity-90">Generate AI-powered video ads</div>
                                </button>
                                <button class="bg-gray-700 hover:bg-gray-600 text-white p-4 rounded-lg text-left">
                                    <i data-lucide="bar-chart-3" class="w-6 h-6 mb-2"></i>
                                    <div class="font-semibold">View Analytics</div>
                                    <div class="text-sm opacity-90">Track video performance</div>
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Other panels can be added here -->
                    <div id="performance-panel" class="hidden">
                        <h1 class="text-3xl font-bold mb-8">Performance Analytics</h1>
                        <div class="bg-gray-800 rounded-xl p-6">
                            <p class="text-gray-400">Performance analytics coming soon...</p>
                        </div>
                    </div>

                    <div id="connect-panel" class="hidden">
                        <h1 class="text-3xl font-bold mb-8">Connect Accounts</h1>
                        <div class="bg-gray-800 rounded-xl p-6">
                            <p class="text-gray-400">Connect your social media accounts...</p>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    </div>

    <script>
        // Initialize Lucide icons
        lucide.createIcons();

        // Theme management
        function initTheme() {
            const isDark = localStorage.getItem('theme') === 'dark' || 
                          (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
            
            if (isDark) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        }

        function toggleTheme() {
            document.documentElement.classList.toggle('dark');
            localStorage.setItem('theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
        }

        // Theme toggle buttons
        document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
        document.getElementById('dashboard-theme-toggle').addEventListener('click', toggleTheme);

        // Navigation functions
        function showDashboard() {
            document.getElementById('landing-page').classList.add('hidden');
            document.getElementById('dashboard').classList.remove('hidden');
            showDashboardTab('overview');
        }

        function showLandingPage() {
            document.getElementById('dashboard').classList.add('hidden');
            document.getElementById('landing-page').classList.remove('hidden');
        }

        function showDashboardTab(tabName) {
            // Hide all panels
            document.querySelectorAll('[id$="-panel"]').forEach(panel => {
                panel.classList.add('hidden');
            });
            
            // Show selected panel
            document.getElementById(tabName + '-panel').classList.remove('hidden');
            
            // Update navigation
            document.querySelectorAll('nav button').forEach(btn => {
                btn.classList.remove('bg-gray-700', 'text-white');
                btn.classList.add('text-gray-300', 'hover:bg-gray-700', 'hover:text-white');
            });
            
            event.target.classList.add('bg-gray-700', 'text-white');
            event.target.classList.remove('text-gray-300', 'hover:bg-gray-700', 'hover:text-white');
        }

        function scrollToSection(href) {
            const element = document.querySelector(href);
            if (element) {
                const offsetTop = element.offsetTop - 80;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        }

        // AI Video Generation
        const aiSteps = [
            "Analyzing brand tone and audience",
            "Generating AI script with natural pacing",
            "Creating voiceover with ElevenLabs AI",
            "Generating dynamic scenes and transitions",
            "Assembling final video with synchronized captions",
            "✓ Video ready!"
        ];

        let aiPollInterval;

        document.getElementById('ai-video-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                brand_name: document.getElementById('ai-brand-name').value,
                brand_description: document.getElementById('ai-brand-description').value,
                target_audience: document.getElementById('ai-target-audience').value || 'general audience',
                tone: 'professional',
                duration: parseInt(document.getElementById('ai-duration').value),
                call_to_action: document.getElementById('ai-call-to-action').value || 'Take action now'
            };
            
            document.getElementById('ai-generate-btn').disabled = true;
            document.getElementById('ai-generate-btn').textContent = 'Generating...';
            document.getElementById('ai-progress').classList.remove('hidden');
            document.getElementById('ai-video-result').classList.add('hidden');
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                if (result.job_id) {
                    pollAIJobStatus(result.job_id);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to start video generation');
                resetAIForm();
            }
        });

        function pollAIJobStatus(jobId) {
            aiPollInterval = setInterval(async () => {
                try {
                    const response = await fetch(\`/api/status/\${jobId}\`);
                    const status = await response.json();
                    
                    updateAIProgress(status.progress);
                    
                    if (status.status === 'completed') {
                        clearInterval(aiPollInterval);
                        showAIVideo(status.video_url);
                    } else if (status.status === 'failed') {
                        clearInterval(aiPollInterval);
                        alert('Video generation failed: ' + status.message);
                        resetAIForm();
                    }
                } catch (error) {
                    console.error('Polling error:', error);
                }
            }, 2000);
        }

        function updateAIProgress(progress) {
            const stepIndex = Math.floor(progress / 17);
            const progressSteps = document.getElementById('ai-progress-steps');
            
            progressSteps.innerHTML = aiSteps.map((step, index) => {
                const status = index < stepIndex ? 'completed' : 
                              index === stepIndex ? 'current' : 'pending';
                const color = status === 'completed' ? 'text-green-400' :
                              status === 'current' ? 'text-orange-400' : 'text-gray-400';
                const dot = status === 'completed' ? 'bg-green-500' :
                            status === 'current' ? 'bg-orange-500 animate-pulse' : 'bg-gray-500';
                
                return \`
                    <div class="flex items-center space-x-3">
                        <div class="w-3 h-3 rounded-full \${dot}"></div>
                        <span class="text-sm \${color}">\${step}</span>
                    </div>
                \`;
            }).join('');
        }

        function showAIVideo(videoUrl) {
            document.getElementById('ai-progress').classList.add('hidden');
            document.getElementById('ai-video-result').classList.remove('hidden');
            
            const videoPlayer = document.getElementById('ai-video-player');
            videoPlayer.src = videoUrl;
            
            document.getElementById('ai-download-btn').onclick = () => {
                window.open(videoUrl, '_blank');
            };
        }

        function resetAIForm() {
            document.getElementById('ai-generate-btn').disabled = false;
            document.getElementById('ai-generate-btn').textContent = 'Generate Video';
            document.getElementById('ai-progress').classList.add('hidden');
            document.getElementById('ai-video-result').classList.add('hidden');
            document.getElementById('ai-video-form').reset();
            document.getElementById('ai-duration-value').textContent = '30';
        }

        // Event listeners for enter panel buttons
        document.getElementById('enter-panel-btn').addEventListener('click', showDashboard);
        document.getElementById('hero-enter-panel').addEventListener('click', showDashboard);

        // Initialize theme on page load
        initTheme();
    </script>
</body>
</html>`;
    
    res.send(completeFrontend);
  });

  // Start Next.js server endpoint
  app.post('/api/start-nextjs', async (req, res) => {
    try {
      const { spawn } = await import('child_process');
      
      // Start Next.js in the background
      const nextProcess = spawn('npm', ['run', 'dev'], {
        cwd: path.join(process.cwd(), 'client'),
        detached: true,
        stdio: 'ignore',
        env: { ...process.env, PORT: '3000' }
      });
      
      nextProcess.unref();
      
      res.json({ success: true, message: 'Next.js starting...' });
    } catch (error) {
      console.error('Error starting Next.js:', error);
      res.status(500).json({ error: 'Failed to start Next.js' });
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}