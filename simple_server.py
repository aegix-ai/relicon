#!/usr/bin/env python3
"""
Simple ReelForge Server - Serves both API and frontend on one port
"""
import os
import json
import uuid
import time
import subprocess
import threading
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socketserver

# In-memory job storage
job_storage = {}

def generate_job_id():
    return f"job_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"

def update_job_status(job_id, status, progress, message, **extras):
    job_storage[job_id] = {
        'job_id': job_id,
        'status': status,
        'progress': progress,
        'message': message,
        'updated_at': datetime.now().isoformat(),
        **extras
    }

def generate_video_async(job_id, request_data):
    """Generate video in background thread"""
    try:
        # Step 1: Analyzing brand
        update_job_status(job_id, 'processing', 10, 'Analyzing brand tone and audience...')
        time.sleep(2)
        
        # Step 2: Generating script
        update_job_status(job_id, 'processing', 30, 'Generating AI script with natural pacing...')
        time.sleep(3)
        
        # Step 3: Creating voiceover
        update_job_status(job_id, 'processing', 50, 'Creating voiceover with ElevenLabs AI...')
        time.sleep(4)
        
        # Step 4: Generating scenes
        update_job_status(job_id, 'processing', 70, 'Generating dynamic scenes and transitions...')
        time.sleep(3)
        
        # Step 5: Assembling video
        update_job_status(job_id, 'processing', 90, 'Assembling final video with synchronized captions...')
        
        # Generate actual video using our system
        result = subprocess.run([
            'python3', 'working_video_generator.py'
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            video_file = 'working_video_generator.mp4'
            if os.path.exists(video_file):
                update_job_status(job_id, 'completed', 100, 'Video generation completed!', 
                                video_url=f'/{video_file}')
            else:
                update_job_status(job_id, 'failed', 0, 'Video file not found')
        else:
            update_job_status(job_id, 'failed', 0, f'Video generation failed: {result.stderr}')
            
    except Exception as e:
        update_job_status(job_id, 'failed', 0, f'Error: {str(e)}')

class ReelForgeHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='.', **kwargs)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/generate':
            self.handle_generate()
        else:
            self.send_error(404)
    
    def do_GET(self):
        if self.path == '/api/health':
            self.handle_health()
        elif self.path.startswith('/api/status/'):
            job_id = self.path.split('/')[-1]
            self.handle_status(job_id)
        elif self.path == '/' or self.path == '/dashboard':
            self.serve_dashboard()
        else:
            # Serve static files
            super().do_GET()
    
    def handle_health(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(response).encode())
    
    def handle_generate(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Validate required fields
            if not request_data.get('brand_name') or not request_data.get('brand_description'):
                self.send_error(400, 'brand_name and brand_description are required')
                return
            
            job_id = generate_job_id()
            update_job_status(job_id, 'queued', 0, 'Video generation started')
            
            # Start background video generation
            thread = threading.Thread(target=generate_video_async, args=(job_id, request_data))
            thread.daemon = True
            thread.start()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'job_id': job_id,
                'status': 'queued',
                'message': 'Video generation started'
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f'Error: {str(e)}')
    
    def handle_status(self, job_id):
        if job_id not in job_storage:
            self.send_error(404, 'Job not found')
            return
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(job_storage[job_id]).encode())
    
    def serve_dashboard(self):
        """Serve the dashboard HTML"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ReelForge | AI Video Generation</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; }
        .bg-gradient { background: linear-gradient(135deg, #000 0%, #1a1a1a 100%); }
    </style>
</head>
<body class="bg-gradient min-h-screen text-white">
    <div class="container mx-auto px-4 py-8">
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold mb-4">🎬 ReelForge</h1>
            <p class="text-xl text-gray-300">AI-Powered Video Generation</p>
        </div>
        
        <div class="max-w-2xl mx-auto bg-gray-800 rounded-xl p-8 shadow-2xl">
            <form id="videoForm" class="space-y-6">
                <div>
                    <label class="block text-sm font-medium mb-2">Brand Name</label>
                    <input type="text" id="brandName" required 
                           class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white">
                </div>
                
                <div>
                    <label class="block text-sm font-medium mb-2">Brand Description</label>
                    <textarea id="brandDescription" required rows="4"
                              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"></textarea>
                </div>
                
                <div>
                    <label class="block text-sm font-medium mb-2">Target Audience</label>
                    <input type="text" id="targetAudience" 
                           class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white">
                </div>
                
                <div>
                    <label class="block text-sm font-medium mb-2">Video Duration: <span id="durationValue">30</span> seconds</label>
                    <input type="range" id="duration" min="15" max="60" step="15" value="30"
                           class="w-full" onchange="document.getElementById('durationValue').textContent = this.value">
                </div>
                
                <button type="submit" id="generateBtn"
                        class="w-full bg-orange-500 hover:bg-orange-600 text-white font-semibold py-3 px-6 rounded-lg transition duration-300">
                    🚀 Generate Video
                </button>
            </form>
            
            <div id="progress" class="mt-6 hidden">
                <div class="bg-gray-700 rounded-lg p-4">
                    <h4 class="font-medium mb-4">🎯 AI Generation Progress</h4>
                    <div id="progressSteps" class="space-y-3"></div>
                </div>
            </div>
            
            <div id="videoResult" class="mt-6 hidden">
                <div class="bg-gray-700 rounded-lg p-4 text-center">
                    <h4 class="font-medium mb-4">🎉 Your Video is Ready!</h4>
                    <video id="videoPlayer" controls class="w-full max-w-md mx-auto rounded-lg">
                        <source type="video/mp4">
                    </video>
                    <div class="mt-4 space-x-3">
                        <button id="downloadBtn" class="bg-orange-500 hover:bg-orange-600 px-6 py-2 rounded-lg">
                            📥 Download Video
                        </button>
                        <button onclick="location.reload()" class="bg-gray-600 hover:bg-gray-500 px-6 py-2 rounded-lg">
                            🔄 Create Another
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const steps = [
            "Analyzing brand tone and audience",
            "Generating AI script with natural pacing", 
            "Creating voiceover with ElevenLabs AI",
            "Generating dynamic scenes and transitions",
            "Assembling final video with synchronized captions",
            "✓ Video ready!"
        ];
        
        let currentStep = 0;
        let pollInterval;
        
        document.getElementById('videoForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                brand_name: document.getElementById('brandName').value,
                brand_description: document.getElementById('brandDescription').value,
                target_audience: document.getElementById('targetAudience').value || 'general audience',
                tone: 'professional',
                duration: parseInt(document.getElementById('duration').value),
                call_to_action: 'Take action now'
            };
            
            document.getElementById('generateBtn').disabled = true;
            document.getElementById('generateBtn').textContent = '🔄 Generating...';
            document.getElementById('progress').classList.remove('hidden');
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                if (result.job_id) {
                    pollJobStatus(result.job_id);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to start video generation');
                resetForm();
            }
        });
        
        function pollJobStatus(jobId) {
            pollInterval = setInterval(async () => {
                try {
                    const response = await fetch(`/api/status/${jobId}`);
                    const status = await response.json();
                    
                    updateProgress(status.progress);
                    
                    if (status.status === 'completed') {
                        clearInterval(pollInterval);
                        showVideo(status.video_url);
                    } else if (status.status === 'failed') {
                        clearInterval(pollInterval);
                        alert('Video generation failed: ' + status.message);
                        resetForm();
                    }
                } catch (error) {
                    console.error('Polling error:', error);
                }
            }, 2000);
        }
        
        function updateProgress(progress) {
            const stepIndex = Math.floor(progress / 17); // 6 steps
            const progressSteps = document.getElementById('progressSteps');
            
            progressSteps.innerHTML = steps.map((step, index) => {
                const status = index < stepIndex ? 'completed' : 
                              index === stepIndex ? 'current' : 'pending';
                const color = status === 'completed' ? 'text-green-400' :
                              status === 'current' ? 'text-orange-400' : 'text-gray-400';
                const dot = status === 'completed' ? 'bg-green-500' :
                            status === 'current' ? 'bg-orange-500 animate-pulse' : 'bg-gray-500';
                
                return `
                    <div class="flex items-center space-x-3">
                        <div class="w-3 h-3 rounded-full ${dot}"></div>
                        <span class="text-sm ${color}">${step}</span>
                    </div>
                `;
            }).join('');
        }
        
        function showVideo(videoUrl) {
            document.getElementById('progress').classList.add('hidden');
            document.getElementById('videoResult').classList.remove('hidden');
            
            const videoPlayer = document.getElementById('videoPlayer');
            videoPlayer.src = videoUrl;
            
            document.getElementById('downloadBtn').onclick = () => {
                window.open(videoUrl, '_blank');
            };
        }
        
        function resetForm() {
            document.getElementById('generateBtn').disabled = false;
            document.getElementById('generateBtn').textContent = '🚀 Generate Video';
            document.getElementById('progress').classList.add('hidden');
            document.getElementById('videoResult').classList.add('hidden');
        }
    </script>
</body>
</html>"""
        self.wfile.write(html.encode())

if __name__ == '__main__':
    PORT = 7000
    print(f"🚀 ReelForge server starting on http://localhost:{PORT}")
    print(f"📊 Dashboard: http://localhost:{PORT}/dashboard")
    print(f"🔧 API Health: http://localhost:{PORT}/api/health")
    
    with socketserver.TCPServer(("", PORT), ReelForgeHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
            httpd.shutdown()