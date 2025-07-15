const { spawn } = require('child_process');
const path = require('path');

// Start Next.js dev server
console.log('Starting Next.js development server...');

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

// Keep the process alive
process.on('SIGINT', () => {
  console.log('Shutting down Next.js server...');
  nextProcess.kill();
  process.exit(0);
});