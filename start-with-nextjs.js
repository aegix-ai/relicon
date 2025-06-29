#!/usr/bin/env node

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import { createProxyMiddleware } from 'http-proxy-middleware';
import express from 'express';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Start Next.js frontend
console.log('Starting Next.js frontend...');
const nextProcess = spawn('npm', ['run', 'dev'], {
  cwd: path.join(__dirname, 'client'),
  stdio: 'inherit',
  env: { ...process.env, PORT: '3000' }
});

// Wait a moment for Next.js to start
setTimeout(() => {
  // Start Express backend
  console.log('Starting Express backend...');
  const backendProcess = spawn('tsx', ['server/index.ts'], {
    stdio: 'inherit',
    env: { ...process.env, NODE_ENV: 'development', FRONTEND_PORT: '3000' }
  });
  
  backendProcess.on('exit', (code) => {
    console.log(`Backend exited with code ${code}`);
    process.exit(code);
  });
}, 3000);

nextProcess.on('exit', (code) => {
  console.log(`Next.js exited with code ${code}`);
  process.exit(code);
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('Shutting down...');
  nextProcess.kill();
  process.exit(0);
});