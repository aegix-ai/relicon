const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Function to check if Next.js is installed and ready
function checkNextJsSetup() {
  const clientDir = path.join(__dirname, 'client');
  const packageJsonPath = path.join(clientDir, 'package.json');
  
  if (!fs.existsSync(packageJsonPath)) {
    console.error('Client package.json not found');
    return false;
  }
  
  return true;
}

// Start the Next.js app
function startNextJs() {
  console.log('Starting Next.js app...');
  
  const nextProcess = spawn('npx', ['next', 'dev', '--port', '3000'], {
    cwd: path.join(__dirname, 'client'),
    stdio: 'inherit',
    env: { ...process.env, NODE_ENV: 'development' }
  });

  nextProcess.on('close', (code) => {
    console.log(`Next.js process exited with code ${code}`);
  });

  nextProcess.on('error', (err) => {
    console.error('Failed to start Next.js:', err);
  });

  return nextProcess;
}

if (checkNextJsSetup()) {
  const nextProcess = startNextJs();
  
  // Handle shutdown
  process.on('SIGINT', () => {
    console.log('Shutting down Next.js server...');
    nextProcess.kill();
    process.exit(0);
  });
} else {
  console.error('Next.js setup verification failed');
  process.exit(1);
}