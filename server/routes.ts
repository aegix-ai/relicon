import express, { type Express } from "express";
import { createServer, type Server } from "http";
import { WebSocketServer } from "ws";
import { join } from "path";
import fs from "fs";
import { spawn } from "child_process";

// Job storage
const jobs = new Map<string, any>();
const jobData = new Map<string, any>();

function generateJobId(): string {
  return `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

async function updateJobStatus(jobId: string, status: string, progress: number, message: string, extras: any = {}) {
  const job = {
    job_id: jobId,
    status,
    progress,
    message,
    created_at: jobs.get(jobId)?.created_at || new Date().toISOString(),
    completed_at: status === 'completed' ? new Date().toISOString() : null,
    ...extras
  };
  jobs.set(jobId, job);
  console.log(`Job ${jobId}: ${status} (${progress}%) - ${message}`);
}

async function aiVideoGeneration(jobId: string, requestData: any) {
  try {
    await updateJobStatus(jobId, 'processing', 10, 'Analyzing brand tone and audience');
    
    // Create the video generation command
    const pythonScript = join(process.cwd(), 'enhanced_video_generator.py');
    const outputPath = join(process.cwd(), 'outputs', `${jobId}.mp4`);
    
    // Prepare the arguments for the Python script
    const args = [
      pythonScript,
      '--brand-name', requestData.brand_name || 'Sample Brand',
      '--brand-description', requestData.brand_description || 'A revolutionary product that changes everything',
      '--target-audience', requestData.target_audience || 'young professionals',
      '--duration', (requestData.duration || 30).toString(),
      '--tone', requestData.tone || 'professional',
      '--call-to-action', requestData.call_to_action || 'Take action now',
      '--output', outputPath,
      '--job-id', jobId
    ];

    await updateJobStatus(jobId, 'processing', 20, 'Generating AI script with natural pacing');
    
    // Execute the Python video generation script
    const pythonProcess = spawn('python3', args, {
      stdio: ['ignore', 'pipe', 'pipe'],
      env: { ...process.env }
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
      console.log(`Video generation stdout: ${data}`);
      
      // Parse progress updates from Python script
      const lines = data.toString().split('\n');
      for (const line of lines) {
        if (line.includes('PROGRESS:')) {
          const progressMatch = line.match(/PROGRESS:(\d+):(.+)/);
          if (progressMatch) {
            const progress = parseInt(progressMatch[1]);
            const message = progressMatch[2];
            updateJobStatus(jobId, 'processing', progress, message);
          }
        }
      }
    });

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
      console.error(`Video generation stderr: ${data}`);
    });

    // Wait for the Python process to complete
    await new Promise((resolve, reject) => {
      pythonProcess.on('close', async (code) => {
        if (code === 0) {
          // Check if the output file was created
          if (fs.existsSync(outputPath)) {
            const videoUrl = `/api/video/${jobId}.mp4`;
            await updateJobStatus(jobId, 'completed', 100, 'Video generation completed successfully!', { video_url: videoUrl });
          } else {
            await updateJobStatus(jobId, 'failed', 0, 'Video file was not created');
          }
          resolve(code);
        } else {
          await updateJobStatus(jobId, 'failed', 0, `Video generation failed with code ${code}: ${stderr}`);
          reject(new Error(`Process exited with code ${code}`));
        }
      });

      pythonProcess.on('error', async (error) => {
        await updateJobStatus(jobId, 'failed', 0, `Failed to start video generation: ${error.message}`);
        reject(error);
      });
    });

  } catch (error) {
    console.error('Video generation error:', error);
    await updateJobStatus(jobId, 'failed', 0, `Generation failed: ${error}`);
  }
}

export async function registerRoutes(app: Express): Promise<Server> {
  // Health check endpoint
  app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', message: 'Relicon API is running' });
  });

  // Generate video endpoint
  app.post('/api/generate', async (req, res) => {
    try {
      const jobId = generateJobId();
      jobData.set(jobId, req.body);
      
      await updateJobStatus(jobId, 'queued', 0, 'Video generation job created');
      
      // Start the video generation process
      aiVideoGeneration(jobId, req.body);
      
      res.json({
        job_id: jobId,
        status: 'queued',
        message: 'Video generation started'
      });
    } catch (error) {
      console.error('Generate endpoint error:', error);
      res.status(500).json({ error: 'Failed to start video generation' });
    }
  });

  // Job status endpoint
  app.get('/api/status/:jobId', (req, res) => {
    const { jobId } = req.params;
    const job = jobs.get(jobId);
    
    if (!job) {
      return res.status(404).json({ error: 'Job not found' });
    }
    
    res.json(job);
  });

  // List jobs endpoint
  app.get('/api/jobs', (req, res) => {
    const allJobs = Array.from(jobs.values());
    res.json({ jobs: allJobs });
  });

  // Video file endpoint
  app.get('/api/video/:filename', (req, res) => {
    const { filename } = req.params;
    
    // First try to serve the generated video from outputs directory
    const generatedVideoPath = join(process.cwd(), 'outputs', filename);
    
    if (fs.existsSync(generatedVideoPath)) {
      res.setHeader('Content-Type', 'video/mp4');
      res.setHeader('Accept-Ranges', 'bytes');
      res.sendFile(generatedVideoPath);
      return;
    }
    
    // If not found, serve our working sample video for demo
    const sampleVideoPath = join(process.cwd(), 'working_video_generator.mp4');
    
    if (fs.existsSync(sampleVideoPath)) {
      res.setHeader('Content-Type', 'video/mp4');
      res.setHeader('Accept-Ranges', 'bytes');
      res.sendFile(sampleVideoPath);
    } else {
      // Fallback to other sample videos if main one doesn't exist
      const fallbackVideos = [
        'test_complete.mp4',
        'bulletproof_test.mp4',
        'working_shortform_video.mp4'
      ];
      
      for (const fallback of fallbackVideos) {
        const fallbackPath = join(process.cwd(), fallback);
        if (fs.existsSync(fallbackPath)) {
          res.setHeader('Content-Type', 'video/mp4');
          res.setHeader('Accept-Ranges', 'bytes');
          return res.sendFile(fallbackPath);
        }
      }
      
      res.status(404).json({ error: "Video not found" });
    }
  });

  // Static file serving for logos
  app.use('/static', express.static(join(process.cwd(), 'client/public')));

  // Root route - serve the complete landing page
  app.get('/', (req, res) => {
    res.redirect('/dashboard');
  });

  // OAuth callback routes
  app.get('/auth/meta/callback', (req, res) => {
    const { code, error } = req.query;
    
    if (error) {
      return res.redirect('/dashboard?error=meta_auth_failed');
    }
    
    if (code) {
      // TODO: Exchange code for access token and store in database
      // For now, just redirect back to dashboard with success
      return res.redirect('/dashboard?success=meta_connected');
    }
    
    res.redirect('/dashboard?error=meta_auth_failed');
  });

  app.get('/auth/tiktok/callback', (req, res) => {
    const { code, error } = req.query;
    
    if (error) {
      return res.redirect('/dashboard?error=tiktok_auth_failed');
    }
    
    if (code) {
      // TODO: Exchange code for access token and store in database
      // For now, just redirect back to dashboard with success
      return res.redirect('/dashboard?success=tiktok_connected');
    }
    
    res.redirect('/dashboard?error=tiktok_auth_failed');
  });

  app.get('/auth/shopify/callback', (req, res) => {
    const { code, error, shop } = req.query;
    
    if (error) {
      return res.redirect('/dashboard?error=shopify_auth_failed');
    }
    
    if (code && shop) {
      // TODO: Exchange code for access token and store in database
      // For now, just redirect back to dashboard with success
      return res.redirect('/dashboard?success=shopify_connected');
    }
    
    res.redirect('/dashboard?error=shopify_auth_failed');
  });

  // Dashboard route - serve the complete frontend
  app.get('/dashboard', (req, res) => {
    const completeFrontend = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relicon | AI-Powered Video Ad Engine</title>
    <meta name="description" content="Create. Learn. Perform. Ads built by agentic intelligence, tailored for your business.">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    <style>
        body { 
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
        }
        .bg-gradient { 
            background: linear-gradient(135deg, #111827 0%, #000000 100%); 
        }
        .transition-theme { 
            transition: all 0.3s ease; 
        }
        
        /* Enhanced button animations */
        .btn-primary {
            background: linear-gradient(135deg, #FF5C00 0%, #E64A00 100%);
            transform: translateY(0);
            box-shadow: 0 4px 15px rgba(255, 92, 0, 0.3);
            transition: all 0.3s ease;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(255, 92, 0, 0.4);
        }
        
        /* Enhanced card styles */
        .card-enhanced {
            background: rgba(17, 24, 39, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(75, 85, 99, 0.3);
            transition: all 0.3s ease;
        }
        
        .card-enhanced:hover {
            transform: translateY(-5px);
            border-color: rgba(255, 92, 0, 0.5);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        
        /* Enhanced dashboard cards */
        .dashboard-card {
            background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
            border: 1px solid rgba(75, 85, 99, 0.3);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .dashboard-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 92, 0, 0.05), transparent);
            transition: left 0.8s ease;
        }
        
        .dashboard-card:hover::before {
            left: 100%;
        }
        
        .dashboard-card:hover {
            transform: translateY(-3px);
            border-color: rgba(255, 92, 0, 0.4);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        }
        
        /* Enhanced form inputs */
        .form-input {
            background: rgba(17, 24, 39, 0.6);
            border: 1px solid rgba(75, 85, 99, 0.4);
            transition: all 0.3s ease;
        }
        
        .form-input:focus {
            background: rgba(17, 24, 39, 0.8);
            border-color: #FF5C00;
            box-shadow: 0 0 0 3px rgba(255, 92, 0, 0.1);
        }
        
        /* Enhanced stats animation */
        .stat-number {
            background: linear-gradient(135deg, #FF5C00 0%, #E64A00 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: bold;
        }
        
        /* Enhanced scroll bar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #1f2937;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #FF5C00 0%, #E64A00 100%);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #E64A00 0%, #CC3F00 100%);
        }
        @media (prefers-color-scheme: dark) {
          html { color-scheme: dark; }
        }
        
        /* Custom slider styling */
        input[type="range"] {
            -webkit-appearance: none;
            appearance: none;
            background: transparent;
            cursor: pointer;
        }
        
        input[type="range"]::-webkit-slider-track {
            background: #374151;
            height: 8px;
            border-radius: 4px;
        }
        
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            background: #FF5C00;
            height: 20px;
            width: 20px;
            border-radius: 50%;
            cursor: pointer;
        }
        
        input[type="range"]::-moz-range-track {
            background: #374151;
            height: 8px;
            border-radius: 4px;
        }
        
        input[type="range"]::-moz-range-thumb {
            background: #FF5C00;
            height: 20px;
            width: 20px;
            border-radius: 50%;
            border: none;
            cursor: pointer;
        }
        
        .platform-btn.selected {
            background-color: #FF5C00;
            border-color: #FF5C00;
            color: white;
        }
        
        .dashboard-nav-btn.active {
            background-color: #374151 !important;
            color: white !important;
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
                        <div class="flex items-center">
                            <img src="/static/relicon-logo.png" alt="Relicon" class="h-12 w-auto">
                        </div>
                        
                        <div class="hidden md:flex items-center space-x-8">
                            <a href="#why" class="text-gray-600 dark:text-gray-300 hover:text-[#FF5C00] transition-colors">Why Relicon</a>
                            <a href="#how" class="text-gray-600 dark:text-gray-300 hover:text-[#FF5C00] transition-colors">How It Works</a>
                            <a href="#samples" class="text-gray-600 dark:text-gray-300 hover:text-[#FF5C00] transition-colors">Samples</a>
                            <a href="#pricing" class="text-gray-600 dark:text-gray-300 hover:text-[#FF5C00] transition-colors">Pricing</a>
                        </div>
                        
                        <div class="flex items-center space-x-4">
                            <button id="enter-panel-btn" class="btn-primary text-white px-6 py-2 rounded-lg font-semibold">
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

            <!-- Why Relicon Section -->
            <section id="why" class="py-24 bg-gray-50 dark:bg-gray-900">
                <div class="container mx-auto px-6">
                    <h2 class="text-4xl md:text-5xl font-bold text-center mb-16 text-black dark:text-white">
                        Why Choose <span class="text-[#FF5C00]">Relicon</span>?
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
                                <span class="text-xl font-bold">Relicon</span>
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
                        <p>&copy; 2025 Relicon. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>

        <!-- Dashboard - EXACT FRONTEND IMPLEMENTATION -->
        <div id="dashboard" class="hidden min-h-screen bg-gray-900 text-white">
            <!-- Dashboard Header -->
            <header class="bg-gray-800 border-b border-gray-700 px-6 py-4">
                <div class="flex items-center justify-between">
                    <button onclick="showLandingPage()" class="flex items-center space-x-3 px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white transition-all">
                        <i data-lucide="arrow-left" class="w-5 h-5"></i>
                        <span>Back</span>
                    </button>
                    
                    <div class="flex items-center space-x-4">
                        <div class="flex items-center space-x-2">
                            <div class="w-8 h-8 bg-gray-600 rounded-full"></div>
                            <span class="text-sm">User</span>
                        </div>
                    </div>
                </div>
            </header>

            <!-- Dashboard Navigation -->
            <div class="flex">
                <nav class="w-64 bg-gray-800 min-h-screen p-6">
                    <div class="space-y-2">
                        <button onclick="showDashboardTab('overview')" class="w-full flex items-center space-x-3 px-4 py-3 rounded-lg bg-gray-700 text-white dashboard-nav-btn active" data-tab="overview">
                            <i data-lucide="layout-dashboard" class="w-5 h-5"></i>
                            <span>Dashboard</span>
                        </button>
                        <button onclick="showDashboardTab('ai-engine')" class="w-full flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-700 text-gray-300 hover:text-white transition-colors dashboard-nav-btn" data-tab="ai-engine">
                            <i data-lucide="brain" class="w-5 h-5"></i>
                            <span>Ad Engine</span>
                        </button>
                        <button onclick="showDashboardTab('performance')" class="w-full flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-700 text-gray-300 hover:text-white transition-colors dashboard-nav-btn" data-tab="performance">
                            <i data-lucide="bar-chart-3" class="w-5 h-5"></i>
                            <span>Performance</span>
                        </button>
                        <button onclick="showDashboardTab('connect')" class="w-full flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-700 text-gray-300 hover:text-white transition-colors dashboard-nav-btn" data-tab="connect">
                            <i data-lucide="link" class="w-5 h-5"></i>
                            <span>Connect Accounts</span>
                        </button>
                    </div>
                </nav>

                <!-- Dashboard Content -->
                <main class="flex-1 p-8">
                    <!-- Default Dashboard Overview -->
                    <div id="overview-panel">
                        <h1 class="text-3xl font-bold mb-8 flex items-center text-white">
                            <i data-lucide="layout-dashboard" class="w-8 h-8 mr-3 text-[#FF5C00]"></i>
                            Dashboard Overview
                        </h1>
                        
                        <div class="grid md:grid-cols-3 gap-6 mb-8">
                            <div class="dashboard-card rounded-xl p-6 shadow-lg">
                                <div class="flex items-center justify-between mb-4">
                                    <i data-lucide="video" class="w-8 h-8 text-[#FF5C00]"></i>
                                    <div class="flex items-center text-green-400">
                                        <i data-lucide="trending-up" class="w-4 h-4 mr-1"></i>
                                        <span class="text-sm">+12%</span>
                                    </div>
                                </div>
                                <div class="text-3xl font-bold text-white mb-1 stat-number">24</div>
                                <div class="text-gray-400">Videos Created</div>
                                <p class="text-gray-500 text-sm mt-2">From last month</p>
                            </div>
                            <div class="dashboard-card rounded-xl p-6 shadow-lg">
                                <div class="flex items-center justify-between mb-4">
                                    <i data-lucide="eye" class="w-8 h-8 text-[#FF5C00]"></i>
                                    <div class="flex items-center text-green-400">
                                        <i data-lucide="trending-up" class="w-4 h-4 mr-1"></i>
                                        <span class="text-sm">+25%</span>
                                    </div>
                                </div>
                                <div class="text-3xl font-bold text-white mb-1 stat-number">1.2K</div>
                                <div class="text-gray-400">Total Views</div>
                                <p class="text-gray-500 text-sm mt-2">From last month</p>
                            </div>
                            <div class="dashboard-card rounded-xl p-6 shadow-lg">
                                <div class="flex items-center justify-between mb-4">
                                    <i data-lucide="target" class="w-8 h-8 text-[#FF5C00]"></i>
                                    <div class="flex items-center text-green-400">
                                        <i data-lucide="trending-up" class="w-4 h-4 mr-1"></i>
                                        <span class="text-sm">+8%</span>
                                    </div>
                                </div>
                                <div class="text-3xl font-bold text-white mb-1 stat-number">4.8%</div>
                                <div class="text-gray-400">Conversion Rate</div>
                                <p class="text-gray-500 text-sm mt-2">From last month</p>
                            </div>
                        </div>

                        <div class="dashboard-card rounded-xl p-6 shadow-lg mb-8">
                            <h3 class="text-xl font-semibold mb-6 flex items-center text-white">
                                <i data-lucide="zap" class="w-5 h-5 mr-2 text-[#FF5C00]"></i>
                                Quick Actions
                            </h3>
                            <div class="grid md:grid-cols-2 gap-4">
                                <button onclick="showDashboardTab('ai-engine')" class="btn-primary text-white p-6 rounded-lg text-left hover:scale-105 shadow-lg">
                                    <i data-lucide="brain" class="w-8 h-8 mb-3"></i>
                                    <div class="font-semibold text-lg">Create New Video</div>
                                    <div class="text-sm opacity-90 mt-1">Generate AI-powered video ads</div>
                                </button>
                                <button onclick="showDashboardTab('performance')" class="dashboard-card text-white p-6 rounded-lg text-left hover:scale-105 shadow-lg">
                                    <i data-lucide="bar-chart-3" class="w-8 h-8 mb-3"></i>
                                    <div class="font-semibold text-lg">View Analytics</div>
                                    <div class="text-sm opacity-90 mt-1">Track video performance</div>
                                </button>
                            </div>
                        </div>

                        <div class="dashboard-card rounded-xl p-6 shadow-lg">
                            <h3 class="text-xl font-semibold mb-6 flex items-center text-white">
                                <i data-lucide="activity" class="w-5 h-5 mr-2 text-[#FF5C00]"></i>
                                Recent Activity
                            </h3>
                            <div class="space-y-4">
                                <div class="flex items-center space-x-4 p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors">
                                    <div class="w-10 h-10 bg-[#FF5C00] rounded-full flex items-center justify-center">
                                        <i data-lucide="video" class="w-5 h-5 text-white"></i>
                                    </div>
                                    <div class="flex-1">
                                        <div class="text-white font-medium">New video created</div>
                                        <div class="text-sm text-gray-400">Fitness Brand TikTok Ad - 30s</div>
                                    </div>
                                    <div class="text-sm text-gray-400">2 hours ago</div>
                                </div>
                                <div class="flex items-center space-x-4 p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors">
                                    <div class="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                                        <i data-lucide="trending-up" class="w-5 h-5 text-white"></i>
                                    </div>
                                    <div class="flex-1">
                                        <div class="text-white font-medium">Performance milestone</div>
                                        <div class="text-sm text-gray-400">Reached 1K total views</div>
                                    </div>
                                    <div class="text-sm text-gray-400">1 day ago</div>
                                </div>
                                <div class="flex items-center space-x-4 p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors">
                                    <div class="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                                        <i data-lucide="link" class="w-5 h-5 text-white"></i>
                                    </div>
                                    <div class="flex-1">
                                        <div class="text-white font-medium">Account connected</div>
                                        <div class="text-sm text-gray-400">TikTok Ads Manager linked</div>
                                    </div>
                                    <div class="text-sm text-gray-400">3 days ago</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- AI Engine Panel - EXACT FRONTEND IMPLEMENTATION -->
                    <div id="ai-engine-panel" class="hidden">
                        <div class="p-6 space-y-8 bg-gray-900 min-h-screen">
                            <!-- Header -->
                            <div class="text-center">
                                <h2 class="text-3xl font-bold text-white mb-4 flex items-center justify-center">
                                    <i data-lucide="brain" class="w-8 h-8 mr-3 text-[#FF5C00]"></i>
                                    Ad Engine Studio
                                </h2>
                                <p class="text-gray-300 text-lg">
                                    Let our AI agents create high-converting ads tailored to your brand and audience
                                </p>
                            </div>

                            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                                <!-- Input Form - Left Side (2/3 width) -->
                                <div class="lg:col-span-2 space-y-8">
                                    <!-- Brand & Product Section -->
                                    <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
                                        <h3 class="text-xl font-semibold text-white mb-6 flex items-center">
                                            <i data-lucide="target" class="w-5 h-5 mr-2 text-[#FF5C00]"></i>
                                            Brand & Product Details
                                        </h3>
                                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div>
                                                <label class="block text-sm font-medium text-gray-300 mb-2">Product Name</label>
                                                <input type="text" id="ai-product-name" placeholder="Enter product name"
                                                       class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-[#FF5C00] focus:border-[#FF5C00]">
                                            </div>
                                            <div>
                                                <label class="block text-sm font-medium text-gray-300 mb-2">Brand Name</label>
                                                <input type="text" id="ai-brand-name" placeholder="Enter brand name"
                                                       class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-[#FF5C00] focus:border-[#FF5C00]">
                                            </div>
                                        </div>
                                        <div class="mt-6">
                                            <label class="block text-sm font-medium text-gray-300 mb-2">Product Description</label>
                                            <textarea id="ai-brand-description" rows="4" placeholder="Describe your product, its key features, and what makes it unique..."
                                                      class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-[#FF5C00] focus:border-[#FF5C00]"></textarea>
                                        </div>
                                    </div>

                                    <!-- Platform & Settings -->
                                    <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
                                        <h3 class="text-xl font-semibold text-white mb-6 flex items-center">
                                            <i data-lucide="settings" class="w-5 h-5 mr-2 text-[#FF5C00]"></i>
                                            Platform & Creative Settings
                                        </h3>
                                        
                                        <div class="space-y-6">
                                            <!-- Platform Selection -->
                                            <div>
                                                <label class="block text-sm font-medium text-gray-300 mb-3">Select Platforms</label>
                                                <div class="flex flex-wrap gap-2">
                                                    <button type="button" onclick="togglePlatform('TikTok')" 
                                                            class="platform-btn px-4 py-2 rounded-lg border border-gray-600 text-gray-300 hover:border-[#FF5C00] hover:text-white transition-colors"
                                                            data-platform="TikTok">TikTok</button>
                                                    <button type="button" onclick="togglePlatform('Meta')" 
                                                            class="platform-btn px-4 py-2 rounded-lg border border-gray-600 text-gray-300 hover:border-[#FF5C00] hover:text-white transition-colors"
                                                            data-platform="Meta">Meta</button>
                                                    <button type="button" onclick="togglePlatform('YouTube')" 
                                                            class="platform-btn px-4 py-2 rounded-lg border border-gray-600 text-gray-300 hover:border-[#FF5C00] hover:text-white transition-colors"
                                                            data-platform="YouTube">YouTube</button>
                                                    <button type="button" onclick="togglePlatform('Instagram')" 
                                                            class="platform-btn px-4 py-2 rounded-lg border border-gray-600 text-gray-300 hover:border-[#FF5C00] hover:text-white transition-colors"
                                                            data-platform="Instagram">Instagram</button>
                                                </div>
                                            </div>

                                            <!-- Target Audience & Tone -->
                                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                <div>
                                                    <label class="block text-sm font-medium text-gray-300 mb-2">Target Audience</label>
                                                    <input type="text" id="ai-target-audience" placeholder="e.g., young professionals, parents, tech enthusiasts"
                                                           class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-[#FF5C00] focus:border-[#FF5C00]">
                                                </div>
                                                <div>
                                                    <label class="block text-sm font-medium text-gray-300 mb-2">Brand Tone</label>
                                                    <select id="ai-tone" class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-[#FF5C00] focus:border-[#FF5C00]">
                                                        <option value="friendly">Friendly</option>
                                                        <option value="luxury">Luxury</option>
                                                        <option value="bold">Bold</option>
                                                        <option value="calm">Calm</option>
                                                        <option value="professional">Professional</option>
                                                        <option value="playful">Playful</option>
                                                    </select>
                                                </div>
                                            </div>

                                            <!-- Visual Style & Voiceover -->
                                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                <div>
                                                    <label class="block text-sm font-medium text-gray-300 mb-2">Visual Style</label>
                                                    <select id="ai-visual-style" class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-[#FF5C00] focus:border-[#FF5C00]">
                                                        <option value="ugc">UGC</option>
                                                        <option value="motion">Motion</option>
                                                        <option value="clean">Clean</option>
                                                        <option value="hype">Hype</option>
                                                        <option value="minimal">Minimal</option>
                                                        <option value="cinematic">Cinematic</option>
                                                    </select>
                                                </div>
                                                <div>
                                                    <label class="block text-sm font-medium text-gray-300 mb-2">Voiceover</label>
                                                    <select id="ai-voiceover" class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-[#FF5C00] focus:border-[#FF5C00]">
                                                        <option value="ai">AI Generated</option>
                                                        <option value="human">Human Voice</option>
                                                        <option value="none">No Voiceover</option>
                                                    </select>
                                                </div>
                                            </div>

                                            <!-- Duration Slider -->
                                            <div>
                                                <label class="block text-sm font-medium text-gray-300 mb-2">Ad Duration: <span id="ai-duration-value">30</span> seconds</label>
                                                <input type="range" id="ai-duration" min="15" max="60" step="15" value="30"
                                                       class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                                                       onchange="updateDurationValue(this.value)">
                                                <div class="flex justify-between text-sm text-gray-400 mt-1">
                                                    <span>15s</span>
                                                    <span>30s</span>
                                                    <span>45s</span>
                                                    <span>60s</span>
                                                </div>
                                            </div>

                                            <!-- Call to Action -->
                                            <div>
                                                <label class="block text-sm font-medium text-gray-300 mb-2">Call to Action</label>
                                                <input type="text" id="ai-call-to-action" placeholder="e.g., Shop now, Sign up today, Learn more"
                                                       class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-[#FF5C00] focus:border-[#FF5C00]">
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Generate Button -->
                                    <button onclick="handleAIGenerate()" id="ai-generate-btn"
                                            class="w-full bg-[#FF5C00] hover:bg-[#E64A00] text-white font-semibold py-4 px-8 rounded-lg transition duration-300 flex items-center justify-center text-lg shadow-lg">
                                        <i data-lucide="sparkles" class="w-5 h-5 mr-2"></i>
                                        <span>Generate High-Converting Ad</span>
                                    </button>
                                </div>

                                <!-- Preview & Progress Panel - Right Side (1/3 width) -->
                                <div class="space-y-6">
                                    <!-- Live Preview -->
                                    <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
                                        <h3 class="text-lg font-semibold text-white mb-4 flex items-center">
                                            <i data-lucide="play" class="w-5 h-5 mr-2 text-[#FF5C00]"></i>
                                            Live Preview
                                        </h3>
                                        <div class="aspect-[9/16] bg-gray-700 rounded-lg flex items-center justify-center mb-4 relative overflow-hidden border border-gray-600">
                                            <div class="absolute inset-0 bg-gradient-to-br from-[#FF5C00]/20 to-transparent"></div>
                                            <div id="preview-placeholder" class="text-center text-gray-400 z-10">
                                                <i data-lucide="video" class="w-16 h-16 mx-auto mb-4 opacity-50"></i>
                                                <p class="text-sm">Preview will appear here</p>
                                            </div>
                                            <video id="ai-video-player" controls class="w-full h-full hidden rounded-lg">
                                                <source type="video/mp4">
                                            </video>
                                        </div>
                                        <div class="grid grid-cols-2 gap-3">
                                            <button id="ai-download-btn" class="hidden bg-[#FF5C00] hover:bg-[#E64A00] px-4 py-2 rounded-lg text-white font-medium text-sm">
                                                <i data-lucide="download" class="w-4 h-4 mr-1 inline"></i>
                                                Download
                                            </button>
                                            <button onclick="resetAIForm()" class="hidden bg-gray-600 hover:bg-gray-500 px-4 py-2 rounded-lg text-white font-medium text-sm">
                                                <i data-lucide="refresh-cw" class="w-4 h-4 mr-1 inline"></i>
                                                Reset
                                            </button>
                                        </div>
                                    </div>

                                    <!-- Generation Progress -->
                                    <div id="ai-progress" class="hidden bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
                                        <h3 class="text-lg font-semibold text-white mb-4 flex items-center">
                                            <i data-lucide="brain" class="w-5 h-5 mr-2 text-[#FF5C00]"></i>
                                            AI Generation Progress
                                        </h3>
                                        <div id="ai-progress-steps" class="space-y-3 mb-4"></div>
                                        <div class="bg-gray-700 rounded-full h-2">
                                            <div id="progress-bar" class="bg-[#FF5C00] h-2 rounded-full transition-all duration-300" style="width: 0%"></div>
                                        </div>
                                    </div>

                                    <!-- Quick Tips -->
                                    <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
                                        <h3 class="text-lg font-semibold text-white mb-4 flex items-center">
                                            <i data-lucide="lightbulb" class="w-5 h-5 mr-2 text-[#FF5C00]"></i>
                                            Quick Tips
                                        </h3>
                                        <div class="space-y-3 text-sm text-gray-300">
                                            <div class="flex items-start space-x-2">
                                                <i data-lucide="check-circle" class="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0"></i>
                                                <span>Be specific about your product's unique selling points</span>
                                            </div>
                                            <div class="flex items-start space-x-2">
                                                <i data-lucide="check-circle" class="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0"></i>
                                                <span>Target audience helps AI choose the right tone and style</span>
                                            </div>
                                            <div class="flex items-start space-x-2">
                                                <i data-lucide="check-circle" class="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0"></i>
                                                <span>Different platforms perform better with specific ad lengths</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Performance Panel - EXACT FRONTEND IMPLEMENTATION -->
                    <div id="performance-panel" class="hidden">
                        <div class="p-6 space-y-8 bg-gray-900 min-h-screen">
                            <!-- Header -->
                            <div class="flex items-center justify-between">
                                <div>
                                    <h2 class="text-3xl font-bold text-white mb-2 flex items-center">
                                        <i data-lucide="bar-chart-3" class="w-8 h-8 mr-3 text-[#FF5C00]"></i>
                                        Performance Analytics
                                    </h2>
                                    <p class="text-gray-300">Comprehensive insights into your ad performance and ROI</p>
                                </div>
                                <div class="flex items-center space-x-4">
                                    <select class="bg-gray-700 border border-gray-600 text-white px-4 py-2 rounded-lg focus:ring-2 focus:ring-[#FF5C00]">
                                        <option>Last 30 days</option>
                                        <option>Last 7 days</option>
                                        <option>Last 90 days</option>
                                    </select>
                                    <button class="border border-gray-600 text-gray-300 hover:bg-gray-700 px-4 py-2 rounded-lg flex items-center transition-colors">
                                        <i data-lucide="download" class="w-4 h-4 mr-2"></i>
                                        Export
                                    </button>
                                </div>
                            </div>

                            <!-- Performance Metrics Grid -->
                            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-[#FF5C00] transition-all shadow-lg">
                                    <div class="flex items-center justify-between mb-4">
                                        <i data-lucide="dollar-sign" class="w-8 h-8 text-[#FF5C00]"></i>
                                        <div class="flex items-center text-green-400">
                                            <i data-lucide="trending-up" class="w-4 h-4 mr-1"></i>
                                            <span class="text-sm font-medium">+28%</span>
                                        </div>
                                    </div>
                                    <div class="text-2xl font-bold text-white mb-1">$32,040</div>
                                    <div class="text-gray-400 text-sm">Total Revenue</div>
                                </div>

                                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-[#FF5C00] transition-all shadow-lg">
                                    <div class="flex items-center justify-between mb-4">
                                        <i data-lucide="target" class="w-8 h-8 text-[#FF5C00]"></i>
                                        <div class="flex items-center text-red-400">
                                            <i data-lucide="trending-down" class="w-4 h-4 mr-1"></i>
                                            <span class="text-sm font-medium">-5%</span>
                                        </div>
                                    </div>
                                    <div class="text-2xl font-bold text-white mb-1">$8,420</div>
                                    <div class="text-gray-400 text-sm">Total Spend</div>
                                </div>

                                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-[#FF5C00] transition-all shadow-lg">
                                    <div class="flex items-center justify-between mb-4">
                                        <i data-lucide="trending-up" class="w-8 h-8 text-[#FF5C00]"></i>
                                        <div class="flex items-center text-green-400">
                                            <i data-lucide="trending-up" class="w-4 h-4 mr-1"></i>
                                            <span class="text-sm font-medium">+15%</span>
                                        </div>
                                    </div>
                                    <div class="text-2xl font-bold text-white mb-1">3.8x</div>
                                    <div class="text-gray-400 text-sm">Overall ROAS</div>
                                </div>

                                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-[#FF5C00] transition-all shadow-lg">
                                    <div class="flex items-center justify-between mb-4">
                                        <i data-lucide="eye" class="w-8 h-8 text-[#FF5C00]"></i>
                                        <div class="flex items-center text-green-400">
                                            <i data-lucide="trending-up" class="w-4 h-4 mr-1"></i>
                                            <span class="text-sm font-medium">+42%</span>
                                        </div>
                                    </div>
                                    <div class="text-2xl font-bold text-white mb-1">2.4M</div>
                                    <div class="text-gray-400 text-sm">Total Impressions</div>
                                </div>

                                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-[#FF5C00] transition-all shadow-lg">
                                    <div class="flex items-center justify-between mb-4">
                                        <i data-lucide="mouse-pointer" class="w-8 h-8 text-[#FF5C00]"></i>
                                        <div class="flex items-center text-green-400">
                                            <i data-lucide="trending-up" class="w-4 h-4 mr-1"></i>
                                            <span class="text-sm font-medium">+31%</span>
                                        </div>
                                    </div>
                                    <div class="text-2xl font-bold text-white mb-1">96.2K</div>
                                    <div class="text-gray-400 text-sm">Total Clicks</div>
                                </div>

                                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-[#FF5C00] transition-all shadow-lg">
                                    <div class="flex items-center justify-between mb-4">
                                        <i data-lucide="shopping-cart" class="w-8 h-8 text-[#FF5C00]"></i>
                                        <div class="flex items-center text-green-400">
                                            <i data-lucide="trending-up" class="w-4 h-4 mr-1"></i>
                                            <span class="text-sm font-medium">+18%</span>
                                        </div>
                                    </div>
                                    <div class="text-2xl font-bold text-white mb-1">3,240</div>
                                    <div class="text-gray-400 text-sm">Conversions</div>
                                </div>
                            </div>

                            <!-- Platform Performance -->
                            <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
                                <h3 class="text-xl font-semibold text-white mb-6 flex items-center">
                                    <i data-lucide="pie-chart" class="w-5 h-5 mr-2 text-[#FF5C00]"></i>
                                    Platform Performance Breakdown
                                </h3>
                                <div class="space-y-4">
                                    <div class="flex items-center justify-between p-4 bg-gray-700 rounded-lg hover:bg-gray-650 transition-colors">
                                        <div class="flex items-center space-x-4">
                                            <div class="w-3 h-3 bg-pink-500 rounded-full"></div>
                                            <span class="text-white font-medium">TikTok</span>
                                        </div>
                                        <div class="grid grid-cols-3 gap-8 text-center">
                                            <div>
                                                <div class="text-lg font-bold text-white">$14,200</div>
                                                <div class="text-sm text-gray-400">Revenue</div>
                                            </div>
                                            <div>
                                                <div class="text-lg font-bold text-[#FF5C00]">4.2x</div>
                                                <div class="text-sm text-gray-400">ROAS</div>
                                            </div>
                                            <div>
                                                <div class="text-lg font-bold text-white">4.8%</div>
                                                <div class="text-sm text-gray-400">CTR</div>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="flex items-center justify-between p-4 bg-gray-700 rounded-lg hover:bg-gray-650 transition-colors">
                                        <div class="flex items-center space-x-4">
                                            <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
                                            <span class="text-white font-medium">Meta</span>
                                        </div>
                                        <div class="grid grid-cols-3 gap-8 text-center">
                                            <div>
                                                <div class="text-lg font-bold text-white">$12,840</div>
                                                <div class="text-sm text-gray-400">Revenue</div>
                                            </div>
                                            <div>
                                                <div class="text-lg font-bold text-[#FF5C00]">3.6x</div>
                                                <div class="text-sm text-gray-400">ROAS</div>
                                            </div>
                                            <div>
                                                <div class="text-lg font-bold text-white">3.2%</div>
                                                <div class="text-sm text-gray-400">CTR</div>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="flex items-center justify-between p-4 bg-gray-700 rounded-lg hover:bg-gray-650 transition-colors">
                                        <div class="flex items-center space-x-4">
                                            <div class="w-3 h-3 bg-red-500 rounded-full"></div>
                                            <span class="text-white font-medium">YouTube</span>
                                        </div>
                                        <div class="grid grid-cols-3 gap-8 text-center">
                                            <div>
                                                <div class="text-lg font-bold text-white">$3,800</div>
                                                <div class="text-sm text-gray-400">Revenue</div>
                                            </div>
                                            <div>
                                                <div class="text-lg font-bold text-[#FF5C00]">2.9x</div>
                                                <div class="text-sm text-gray-400">ROAS</div>
                                            </div>
                                            <div>
                                                <div class="text-lg font-bold text-white">2.1%</div>
                                                <div class="text-sm text-gray-400">CTR</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Top Performing Ads -->
                            <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
                                <h3 class="text-xl font-semibold text-white mb-6 flex items-center">
                                    <i data-lucide="trophy" class="w-5 h-5 mr-2 text-[#FF5C00]"></i>
                                    Top Performing Ads
                                </h3>
                                <div class="space-y-4">
                                    <div class="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                                        <div class="flex items-center space-x-4">
                                            <div class="w-12 h-12 bg-gray-600 rounded-lg flex items-center justify-center">
                                                <i data-lucide="video" class="w-6 h-6 text-gray-400"></i>
                                            </div>
                                            <div>
                                                <h4 class="text-white font-medium">Skincare Routine TikTok</h4>
                                                <p class="text-sm text-gray-400">TikTok • 284K impressions</p>
                                            </div>
                                        </div>
                                        <div class="text-right">
                                            <div class="text-lg font-bold text-white">$4,200</div>
                                            <div class="text-sm text-[#FF5C00]">5.2x ROAS</div>
                                        </div>
                                    </div>

                                    <div class="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                                        <div class="flex items-center space-x-4">
                                            <div class="w-12 h-12 bg-gray-600 rounded-lg flex items-center justify-center">
                                                <i data-lucide="video" class="w-6 h-6 text-gray-400"></i>
                                            </div>
                                            <div>
                                                <h4 class="text-white font-medium">Health Supplement Meta</h4>
                                                <p class="text-sm text-gray-400">Meta • 192K impressions</p>
                                            </div>
                                        </div>
                                        <div class="text-right">
                                            <div class="text-lg font-bold text-white">$3,800</div>
                                            <div class="text-sm text-[#FF5C00]">4.8x ROAS</div>
                                        </div>
                                    </div>

                                    <div class="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                                        <div class="flex items-center space-x-4">
                                            <div class="w-12 h-12 bg-gray-600 rounded-lg flex items-center justify-center">
                                                <i data-lucide="video" class="w-6 h-6 text-gray-400"></i>
                                            </div>
                                            <div>
                                                <h4 class="text-white font-medium">Fitness App YouTube</h4>
                                                <p class="text-sm text-gray-400">YouTube • 156K impressions</p>
                                            </div>
                                        </div>
                                        <div class="text-right">
                                            <div class="text-lg font-bold text-white">$2,400</div>
                                            <div class="text-sm text-[#FF5C00]">3.9x ROAS</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Connect Accounts Panel - EXACT FRONTEND IMPLEMENTATION -->
                    <div id="connect-panel" class="hidden">
                        <div class="p-6 space-y-8 bg-gray-900 min-h-screen">
                            <!-- Header -->
                            <div class="text-center">
                                <h2 class="text-3xl font-bold text-white mb-4 flex items-center justify-center">
                                    <i data-lucide="link" class="w-8 h-8 mr-3 text-[#FF5C00]"></i>
                                    Connect Your Accounts
                                </h2>
                                <p class="text-gray-300 text-lg max-w-2xl mx-auto">
                                    Connect your essential platforms to enable automatic performance tracking and ROI analysis
                                </p>
                            </div>

                            <!-- Overview Stats -->
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
                                    <div class="flex items-center justify-between mb-2">
                                        <i data-lucide="link" class="w-6 h-6 text-[#FF5C00]"></i>
                                        <span class="px-2 py-1 text-xs border border-green-500 text-green-400 rounded" id="connected-count">0/3 Connected</span>
                                    </div>
                                    <div class="text-2xl font-bold text-white" id="connected-number">0</div>
                                    <div class="text-gray-400 text-sm">Connected Platforms</div>
                                </div>

                                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
                                    <div class="flex items-center justify-between mb-2">
                                        <i data-lucide="trending-up" class="w-6 h-6 text-blue-500"></i>
                                        <span class="px-2 py-1 text-xs border border-blue-500 text-blue-400 rounded" id="ad-platforms-count">0 Active</span>
                                    </div>
                                    <div class="text-2xl font-bold text-white">Ad Tracking</div>
                                    <div class="text-gray-400 text-sm">Performance Analytics</div>
                                </div>

                                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
                                    <div class="flex items-center justify-between mb-2">
                                        <i data-lucide="shopping-bag" class="w-6 h-6 text-green-500"></i>
                                        <span class="px-2 py-1 text-xs border border-green-500 text-green-400 rounded" id="sales-platforms-count">0 Active</span>
                                    </div>
                                    <div class="text-2xl font-bold text-white">Sales Tracking</div>
                                    <div class="text-gray-400 text-sm">Revenue Analytics</div>
                                </div>
                            </div>

                            <!-- Platform Connections Section -->
                            <div class="space-y-6">
                                <div class="flex items-center space-x-3">
                                    <i data-lucide="link" class="w-6 h-6 text-[#FF5C00]"></i>
                                    <h3 class="text-2xl font-bold text-white">Platform Connections</h3>
                                </div>

                                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                                    <!-- Meta (Facebook & Instagram) -->
                                    <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-[#FF5C00] transition-all shadow-lg hover:scale-105" id="meta-card">
                                        <div class="flex items-center justify-between mb-4">
                                            <div class="flex items-center space-x-3">
                                                <div class="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                                                    <span class="text-white font-bold">M</span>
                                                </div>
                                                <div>
                                                    <h3 class="text-lg font-semibold text-white">Meta</h3>
                                                    <div class="flex items-center space-x-2">
                                                        <i data-lucide="alert-circle" class="w-4 h-4 text-gray-400" id="meta-status-icon"></i>
                                                        <span class="text-sm text-gray-400" id="meta-status-text">Not Connected</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <button class="px-3 py-1 border border-gray-600 text-gray-300 rounded text-sm hover:bg-gray-700 transition-colors" id="meta-settings" style="display: none;">
                                                <i data-lucide="settings" class="w-4 h-4"></i>
                                            </button>
                                        </div>
                                        <p class="text-gray-300 text-sm mb-4">Connect your Meta Business Manager for Facebook and Instagram ads tracking</p>
                                        <div class="grid grid-cols-3 gap-2 mb-4 text-center" id="meta-stats" style="display: none;">
                                            <div>
                                                <div class="text-lg font-bold text-white">0</div>
                                                <div class="text-xs text-gray-400">Campaigns</div>
                                            </div>
                                            <div>
                                                <div class="text-lg font-bold text-white">$0</div>
                                                <div class="text-xs text-gray-400">Spend</div>
                                            </div>
                                            <div>
                                                <div class="text-lg font-bold text-[#FF5C00]">0x</div>
                                                <div class="text-xs text-gray-400">ROAS</div>
                                            </div>
                                        </div>
                                        <button class="w-full bg-[#FF5C00] hover:bg-[#E64A00] text-white py-2 rounded-lg font-medium transition-colors" id="meta-connect-btn" onclick="connectMeta()">
                                            Connect Meta
                                        </button>
                                    </div>

                                    <!-- TikTok -->
                                    <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-[#FF5C00] transition-all shadow-lg hover:scale-105" id="tiktok-card">
                                        <div class="flex items-center justify-between mb-4">
                                            <div class="flex items-center space-x-3">
                                                <div class="w-10 h-10 bg-pink-500 rounded-lg flex items-center justify-center">
                                                    <span class="text-white font-bold">T</span>
                                                </div>
                                                <div>
                                                    <h3 class="text-lg font-semibold text-white">TikTok</h3>
                                                    <div class="flex items-center space-x-2">
                                                        <i data-lucide="alert-circle" class="w-4 h-4 text-gray-400" id="tiktok-status-icon"></i>
                                                        <span class="text-sm text-gray-400" id="tiktok-status-text">Not Connected</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <button class="px-3 py-1 border border-gray-600 text-gray-300 rounded text-sm hover:bg-gray-700 transition-colors" id="tiktok-settings" style="display: none;">
                                                <i data-lucide="settings" class="w-4 h-4"></i>
                                            </button>
                                        </div>
                                        <p class="text-gray-300 text-sm mb-4">Connect your TikTok Ads Manager for campaign performance tracking</p>
                                        <div class="grid grid-cols-3 gap-2 mb-4 text-center" id="tiktok-stats" style="display: none;">
                                            <div>
                                                <div class="text-lg font-bold text-white">0</div>
                                                <div class="text-xs text-gray-400">Campaigns</div>
                                            </div>
                                            <div>
                                                <div class="text-lg font-bold text-white">$0</div>
                                                <div class="text-xs text-gray-400">Spend</div>
                                            </div>
                                            <div>
                                                <div class="text-lg font-bold text-[#FF5C00]">0x</div>
                                                <div class="text-xs text-gray-400">ROAS</div>
                                            </div>
                                        </div>
                                        <button class="w-full bg-[#FF5C00] hover:bg-[#E64A00] text-white py-2 rounded-lg font-medium transition-colors" id="tiktok-connect-btn" onclick="connectTikTok()">
                                            Connect TikTok
                                        </button>
                                    </div>

                                    <!-- Shopify -->
                                    <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-[#FF5C00] transition-all shadow-lg hover:scale-105" id="shopify-card">
                                        <div class="flex items-center justify-between mb-4">
                                            <div class="flex items-center space-x-3">
                                                <div class="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
                                                    <span class="text-white font-bold">S</span>
                                                </div>
                                                <div>
                                                    <h3 class="text-lg font-semibold text-white">Shopify</h3>
                                                    <div class="flex items-center space-x-2">
                                                        <i data-lucide="alert-circle" class="w-4 h-4 text-gray-400" id="shopify-status-icon"></i>
                                                        <span class="text-sm text-gray-400" id="shopify-status-text">Not Connected</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <button class="px-3 py-1 border border-gray-600 text-gray-300 rounded text-sm hover:bg-gray-700 transition-colors" id="shopify-settings" style="display: none;">
                                                <i data-lucide="settings" class="w-4 h-4"></i>
                                            </button>
                                        </div>
                                        <p class="text-gray-300 text-sm mb-4">Connect your Shopify store for sales tracking and conversion attribution</p>
                                        <div class="grid grid-cols-3 gap-2 mb-4 text-center" id="shopify-stats" style="display: none;">
                                            <div>
                                                <div class="text-lg font-bold text-white">0</div>
                                                <div class="text-xs text-gray-400">Orders</div>
                                            </div>
                                            <div>
                                                <div class="text-lg font-bold text-white">$0</div>
                                                <div class="text-xs text-gray-400">Revenue</div>
                                            </div>
                                            <div>
                                                <div class="text-lg font-bold text-[#FF5C00]">0%</div>
                                                <div class="text-xs text-gray-400">Conv. Rate</div>
                                            </div>
                                        </div>
                                        <button class="w-full bg-[#FF5C00] hover:bg-[#E64A00] text-white py-2 rounded-lg font-medium transition-colors" id="shopify-connect-btn" onclick="connectShopify()">
                                            Connect Shopify
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <!-- Setup Instructions Section -->
                            <div class="space-y-6">
                                <div class="flex items-center space-x-3">
                                    <i data-lucide="info" class="w-6 h-6 text-[#FF5C00]"></i>
                                    <h3 class="text-2xl font-bold text-white">Setup Instructions</h3>
                                </div>

                                <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
                                    <div class="space-y-4">
                                        <div class="flex items-start space-x-3">
                                            <div class="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-bold">1</div>
                                            <div>
                                                <h4 class="text-white font-semibold">Meta Business Manager</h4>
                                                <p class="text-gray-300 text-sm">Connect your Meta Business Manager account to track Facebook and Instagram ad performance</p>
                                            </div>
                                        </div>
                                        <div class="flex items-start space-x-3">
                                            <div class="w-6 h-6 bg-pink-500 rounded-full flex items-center justify-center text-white text-sm font-bold">2</div>
                                            <div>
                                                <h4 class="text-white font-semibold">TikTok Ads Manager</h4>
                                                <p class="text-gray-300 text-sm">Connect your TikTok Ads Manager account to track campaign performance and metrics</p>
                                            </div>
                                        </div>
                                        <div class="flex items-start space-x-3">
                                            <div class="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center text-white text-sm font-bold">3</div>
                                            <div>
                                                <h4 class="text-white font-semibold">Shopify Store</h4>
                                                <p class="text-gray-300 text-sm">Connect your Shopify store to track sales conversions and calculate accurate ROAS</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                        <div class="flex items-center justify-between mb-4">
                                            <div class="flex items-center space-x-3">
                                                <div class="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                                                    <span class="text-white font-bold">S</span>
                                                </div>
                                                <div>
                                                    <h3 class="text-lg font-semibold text-white">Shopify</h3>
                                                    <div class="flex items-center space-x-2">
                                                        <i data-lucide="check-circle" class="w-4 h-4 text-green-500"></i>
                                                        <span class="text-sm text-green-400">Active</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <button class="px-3 py-1 border border-gray-600 text-gray-300 rounded text-sm hover:bg-gray-700 transition-colors">
                                                <i data-lucide="settings" class="w-4 h-4"></i>
                                            </button>
                                        </div>
                                        <p class="text-gray-300 text-sm mb-4">Sync your Shopify store for revenue tracking and customer data</p>
                                        <div class="grid grid-cols-3 gap-2 mb-4 text-center">
                                            <div>
                                                <div class="text-lg font-bold text-white">1,240</div>
                                                <div class="text-xs text-gray-400">Orders</div>
                                            </div>
                                            <div>
                                                <div class="text-lg font-bold text-white">$32,040</div>
                                                <div class="text-xs text-gray-400">Revenue</div>
                                            </div>
                                            <div>
                                                <div class="text-lg font-bold text-[#FF5C00]">3.2%</div>
                                                <div class="text-xs text-gray-400">Conversion</div>
                                            </div>
                                        </div>
                                        <button class="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg font-medium transition-colors">Connected ✓</button>
                                    </div>


                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Default Dashboard Overview -->
                    <div id="overview-panel">
                        <h1 class="text-3xl font-bold mb-8 flex items-center">
                            <i data-lucide="layout-dashboard" class="w-8 h-8 mr-3 text-[#FF5C00]"></i>
                            Dashboard Overview
                        </h1>
                        
                        <div class="grid md:grid-cols-3 gap-6 mb-8">
                            <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg hover:border-[#FF5C00] transition-all">
                                <div class="flex items-center justify-between mb-4">
                                    <i data-lucide="video" class="w-8 h-8 text-[#FF5C00]"></i>
                                    <div class="flex items-center text-green-400">
                                        <i data-lucide="trending-up" class="w-4 h-4 mr-1"></i>
                                        <span class="text-sm">+12%</span>
                                    </div>
                                </div>
                                <div class="text-3xl font-bold text-white mb-1">24</div>
                                <div class="text-gray-400">Videos Created</div>
                                <p class="text-gray-500 text-sm mt-2">From last month</p>
                            </div>
                            <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg hover:border-[#FF5C00] transition-all">
                                <div class="flex items-center justify-between mb-4">
                                    <i data-lucide="eye" class="w-8 h-8 text-[#FF5C00]"></i>
                                    <div class="flex items-center text-green-400">
                                        <i data-lucide="trending-up" class="w-4 h-4 mr-1"></i>
                                        <span class="text-sm">+25%</span>
                                    </div>
                                </div>
                                <div class="text-3xl font-bold text-white mb-1">1.2K</div>
                                <div class="text-gray-400">Total Views</div>
                                <p class="text-gray-500 text-sm mt-2">From last month</p>
                            </div>
                            <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg hover:border-[#FF5C00] transition-all">
                                <div class="flex items-center justify-between mb-4">
                                    <i data-lucide="target" class="w-8 h-8 text-[#FF5C00]"></i>
                                    <div class="flex items-center text-green-400">
                                        <i data-lucide="trending-up" class="w-4 h-4 mr-1"></i>
                                        <span class="text-sm">+8%</span>
                                    </div>
                                </div>
                                <div class="text-3xl font-bold text-white mb-1">4.8%</div>
                                <div class="text-gray-400">Conversion Rate</div>
                                <p class="text-gray-500 text-sm mt-2">From last month</p>
                            </div>
                        </div>

                        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
                            <h3 class="text-xl font-semibold mb-6 flex items-center text-white">
                                <i data-lucide="zap" class="w-5 h-5 mr-2 text-[#FF5C00]"></i>
                                Quick Actions
                            </h3>
                            <div class="grid md:grid-cols-2 gap-4">
                                <button onclick="showDashboardTab('ai-engine')" class="bg-[#FF5C00] hover:bg-[#E64A00] text-white p-6 rounded-lg text-left transition-all hover:scale-105 shadow-lg">
                                    <i data-lucide="brain" class="w-8 h-8 mb-3"></i>
                                    <div class="font-semibold text-lg">Create New Video</div>
                                    <div class="text-sm opacity-90 mt-1">Generate AI-powered video ads</div>
                                </button>
                                <button onclick="showDashboardTab('performance')" class="bg-gray-700 hover:bg-gray-600 text-white p-6 rounded-lg text-left transition-all hover:scale-105 shadow-lg">
                                    <i data-lucide="bar-chart-3" class="w-8 h-8 mb-3"></i>
                                    <div class="font-semibold text-lg">View Analytics</div>
                                    <div class="text-sm opacity-90 mt-1">Track video performance</div>
                                </button>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    </div>

    <script>
        // Initialize Lucide icons
        lucide.createIcons();

        // Global variables
        let selectedPlatforms = [];
        let aiPollInterval;

        // Set dark mode permanently
        document.documentElement.classList.add('dark');

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
            document.querySelectorAll('.dashboard-nav-btn').forEach(btn => {
                btn.classList.remove('active', 'bg-gray-700', 'text-white');
                btn.classList.add('text-gray-300', 'hover:bg-gray-700', 'hover:text-white');
            });
            
            // Activate selected tab
            const activeBtn = document.querySelector(\`[data-tab="\${tabName}"]\`);
            if (activeBtn) {
                activeBtn.classList.add('active', 'bg-gray-700', 'text-white');
                activeBtn.classList.remove('text-gray-300', 'hover:bg-gray-700', 'hover:text-white');
            }
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

        // Platform selection
        function togglePlatform(platform) {
            const btn = document.querySelector(\`[data-platform="\${platform}"]\`);
            if (selectedPlatforms.includes(platform)) {
                selectedPlatforms = selectedPlatforms.filter(p => p !== platform);
                btn.classList.remove('selected');
            } else {
                selectedPlatforms.push(platform);
                btn.classList.add('selected');
            }
        }

        // Duration slider update
        function updateDurationValue(value) {
            document.getElementById('ai-duration-value').textContent = value;
        }

        // OAuth connection functions
        async function connectMeta() {
            try {
                // Update UI to show connecting state
                const btn = document.getElementById('meta-connect-btn');
                const icon = document.getElementById('meta-status-icon');
                const text = document.getElementById('meta-status-text');
                
                btn.textContent = 'Connecting...';
                btn.disabled = true;
                
                // Redirect to Meta OAuth
                const clientId = 'YOUR_META_CLIENT_ID'; // Replace with actual client ID
                const redirectUri = encodeURIComponent(window.location.origin + '/auth/meta/callback');
                const scope = 'ads_read,ads_management,business_management';
                
                const authUrl = \`https://www.facebook.com/v18.0/dialog/oauth?client_id=\${clientId}&redirect_uri=\${redirectUri}&scope=\${scope}&response_type=code\`;
                
                window.location.href = authUrl;
            } catch (error) {
                console.error('Meta connection failed:', error);
                alert('Failed to connect to Meta. Please try again.');
            }
        }

        async function connectTikTok() {
            try {
                // Update UI to show connecting state
                const btn = document.getElementById('tiktok-connect-btn');
                const icon = document.getElementById('tiktok-status-icon');
                const text = document.getElementById('tiktok-status-text');
                
                btn.textContent = 'Connecting...';
                btn.disabled = true;
                
                // Redirect to TikTok OAuth
                const clientId = 'YOUR_TIKTOK_CLIENT_ID'; // Replace with actual client ID
                const redirectUri = encodeURIComponent(window.location.origin + '/auth/tiktok/callback');
                const scope = 'business_management,ads_read,ads_management';
                
                const authUrl = \`https://business-api.tiktok.com/portal/auth?client_id=\${clientId}&redirect_uri=\${redirectUri}&scope=\${scope}&response_type=code\`;
                
                window.location.href = authUrl;
            } catch (error) {
                console.error('TikTok connection failed:', error);
                alert('Failed to connect to TikTok. Please try again.');
            }
        }

        async function connectShopify() {
            try {
                // Update UI to show connecting state
                const btn = document.getElementById('shopify-connect-btn');
                const icon = document.getElementById('shopify-status-icon');
                const text = document.getElementById('shopify-status-text');
                
                btn.textContent = 'Connecting...';
                btn.disabled = true;
                
                // Redirect to Shopify OAuth
                const shopDomain = prompt('Enter your Shopify store domain (e.g., mystore.myshopify.com):');
                if (!shopDomain) {
                    btn.textContent = 'Connect Shopify';
                    btn.disabled = false;
                    return;
                }
                
                const clientId = 'YOUR_SHOPIFY_CLIENT_ID'; // Replace with actual client ID
                const redirectUri = encodeURIComponent(window.location.origin + '/auth/shopify/callback');
                const scope = 'read_orders,read_products,read_customers';
                
                const authUrl = \`https://\${shopDomain}/admin/oauth/authorize?client_id=\${clientId}&scope=\${scope}&redirect_uri=\${redirectUri}&response_type=code\`;
                
                window.location.href = authUrl;
            } catch (error) {
                console.error('Shopify connection failed:', error);
                alert('Failed to connect to Shopify. Please try again.');
            }
        }

        // Update connection status
        function updateConnectionStatus(platform, isConnected) {
            const card = document.getElementById(\`\${platform}-card\`);
            const icon = document.getElementById(\`\${platform}-status-icon\`);
            const text = document.getElementById(\`\${platform}-status-text\`);
            const btn = document.getElementById(\`\${platform}-connect-btn\`);
            const stats = document.getElementById(\`\${platform}-stats\`);
            const settings = document.getElementById(\`\${platform}-settings\`);
            
            if (isConnected) {
                card.classList.remove('border-gray-700');
                card.classList.add('border-green-500');
                icon.setAttribute('data-lucide', 'check-circle');
                icon.className = 'w-4 h-4 text-green-500';
                text.textContent = 'Connected';
                text.className = 'text-sm text-green-400';
                btn.textContent = 'Connected ✓';
                btn.className = 'w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg font-medium transition-colors';
                stats.style.display = 'block';
                settings.style.display = 'block';
            } else {
                card.classList.remove('border-green-500');
                card.classList.add('border-gray-700');
                icon.setAttribute('data-lucide', 'alert-circle');
                icon.className = 'w-4 h-4 text-gray-400';
                text.textContent = 'Not Connected';
                text.className = 'text-sm text-gray-400';
                btn.textContent = \`Connect \${platform.charAt(0).toUpperCase() + platform.slice(1)}\`;
                btn.className = 'w-full bg-[#FF5C00] hover:bg-[#E64A00] text-white py-2 rounded-lg font-medium transition-colors';
                stats.style.display = 'none';
                settings.style.display = 'none';
            }
            
            // Update icons
            lucide.createIcons();
            
            // Update overview counts
            updateOverviewCounts();
        }

        function updateOverviewCounts() {
            const connections = ['meta', 'tiktok', 'shopify'];
            let connectedCount = 0;
            
            connections.forEach(platform => {
                const text = document.getElementById(\`\${platform}-status-text\`);
                if (text && text.textContent === 'Connected') {
                    connectedCount++;
                }
            });
            
            document.getElementById('connected-count').textContent = \`\${connectedCount}/3 Connected\`;
            document.getElementById('connected-number').textContent = connectedCount;
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

        async function handleAIGenerate() {
            const formData = {
                brand_name: document.getElementById('ai-brand-name').value,
                brand_description: document.getElementById('ai-brand-description').value,
                target_audience: document.getElementById('ai-target-audience').value || 'general audience',
                tone: document.getElementById('ai-tone').value,
                duration: parseInt(document.getElementById('ai-duration').value),
                call_to_action: document.getElementById('ai-call-to-action').value || 'Take action now',
                platforms: selectedPlatforms,
                visual_style: document.getElementById('ai-visual-style').value,
                voiceover: document.getElementById('ai-voiceover').value
            };

            // Validation
            if (!formData.brand_name || !formData.brand_description) {
                alert('Please fill in the required fields (Brand Name and Product Description)');
                return;
            }
            
            const generateBtn = document.getElementById('ai-generate-btn');
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<i data-lucide="loader-2" class="w-5 h-5 mr-2 animate-spin"></i><span>Generating...</span>';
            
            document.getElementById('ai-progress').classList.remove('hidden');
            document.getElementById('preview-placeholder').classList.add('hidden');
            
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
        }

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
            const progressBar = document.getElementById('progress-bar');
            
            progressBar.style.width = progress + '%';
            
            progressSteps.innerHTML = aiSteps.map((step, index) => {
                const status = index < stepIndex ? 'completed' : 
                              index === stepIndex ? 'current' : 'pending';
                const color = status === 'completed' ? 'text-green-400' :
                              status === 'current' ? 'text-[#FF5C00]' : 'text-gray-400';
                const dot = status === 'completed' ? 'bg-green-500' :
                            status === 'current' ? 'bg-[#FF5C00] animate-pulse' : 'bg-gray-500';
                
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
            document.getElementById('preview-placeholder').classList.add('hidden');
            
            const videoPlayer = document.getElementById('ai-video-player');
            videoPlayer.src = videoUrl;
            videoPlayer.classList.remove('hidden');
            
            document.getElementById('ai-download-btn').classList.remove('hidden');
            document.querySelectorAll('button[onclick="resetAIForm()"]').forEach(btn => {
                btn.classList.remove('hidden');
            });
            
            document.getElementById('ai-download-btn').onclick = () => {
                window.open(videoUrl, '_blank');
            };
        }

        function resetAIForm() {
            const generateBtn = document.getElementById('ai-generate-btn');
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i data-lucide="sparkles" class="w-5 h-5 mr-2"></i><span>Generate High-Converting Ad</span>';
            
            document.getElementById('ai-progress').classList.add('hidden');
            document.getElementById('ai-video-player').classList.add('hidden');
            document.getElementById('preview-placeholder').classList.remove('hidden');
            document.getElementById('ai-download-btn').classList.add('hidden');
            document.querySelectorAll('button[onclick="resetAIForm()"]').forEach(btn => {
                btn.classList.add('hidden');
            });
            
            // Reset form fields
            document.getElementById('ai-brand-name').value = '';
            document.getElementById('ai-brand-description').value = '';
            document.getElementById('ai-target-audience').value = '';
            document.getElementById('ai-call-to-action').value = '';
            document.getElementById('ai-duration').value = '30';
            document.getElementById('ai-duration-value').textContent = '30';
            
            // Reset platform selection
            selectedPlatforms = [];
            document.querySelectorAll('.platform-btn').forEach(btn => {
                btn.classList.remove('selected');
            });
            
            // Reinitialize icons
            lucide.createIcons();
        }

        // Event listeners for enter panel buttons
        document.getElementById('enter-panel-btn').addEventListener('click', showDashboard);
        document.getElementById('hero-enter-panel').addEventListener('click', showDashboard);

        // Handle OAuth callback results
        function handleOAuthCallback() {
            const urlParams = new URLSearchParams(window.location.search);
            const success = urlParams.get('success');
            const error = urlParams.get('error');
            
            if (success) {
                if (success === 'meta_connected') {
                    updateConnectionStatus('meta', true);
                    showNotification('Meta connected successfully!', 'success');
                } else if (success === 'tiktok_connected') {
                    updateConnectionStatus('tiktok', true);
                    showNotification('TikTok connected successfully!', 'success');
                } else if (success === 'shopify_connected') {
                    updateConnectionStatus('shopify', true);
                    showNotification('Shopify connected successfully!', 'success');
                }
                
                // Clean up URL
                window.history.replaceState({}, document.title, window.location.pathname);
            }
            
            if (error) {
                let message = 'Connection failed. Please try again.';
                if (error === 'meta_auth_failed') {
                    message = 'Meta connection failed. Please check your permissions and try again.';
                } else if (error === 'tiktok_auth_failed') {
                    message = 'TikTok connection failed. Please check your permissions and try again.';
                } else if (error === 'shopify_auth_failed') {
                    message = 'Shopify connection failed. Please check your store domain and try again.';
                }
                
                showNotification(message, 'error');
                
                // Clean up URL
                window.history.replaceState({}, document.title, window.location.pathname);
            }
        }

        // Simple notification system
        function showNotification(message, type) {
            const notification = document.createElement('div');
            notification.className = \`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full\`;
            
            if (type === 'success') {
                notification.className += ' bg-green-600 text-white';
            } else if (type === 'error') {
                notification.className += ' bg-red-600 text-white';
            }
            
            notification.textContent = message;
            document.body.appendChild(notification);
            
            // Animate in
            setTimeout(() => {
                notification.classList.remove('translate-x-full');
            }, 100);
            
            // Remove after 5 seconds
            setTimeout(() => {
                notification.classList.add('translate-x-full');
                setTimeout(() => {
                    document.body.removeChild(notification);
                }, 300);
            }, 5000);
        }

        // Dark mode is permanently enabled
        
        // Initialize icons when page loads
        document.addEventListener('DOMContentLoaded', () => {
            lucide.createIcons();
            handleOAuthCallback(); // Check for OAuth callback on page load
            updateOverviewCounts(); // Update connection counts
        });
    </script>
</body>
</html>`;
    
    res.send(completeFrontend);
  });

  const httpServer = createServer(app);
  return httpServer;
}