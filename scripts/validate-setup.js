#!/usr/bin/env node

/**
 * Relicon Setup Validation Script
 *
 * This script checks:
 * 1. Environment variables are configured
 * 2. Database connection works
 * 3. API keys are valid
 * 4. Backend is accessible
 *
 * Usage: node scripts/validate-setup.js
 */

const fs = require('fs');
const path = require('path');

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function success(message) {
  console.log(`${colors.green}✓${colors.reset} ${message}`);
}

function error(message) {
  console.log(`${colors.red}✗${colors.reset} ${message}`);
}

function warning(message) {
  console.log(`${colors.yellow}⚠${colors.reset} ${message}`);
}

function info(message) {
  console.log(`${colors.blue}ℹ${colors.reset} ${message}`);
}

// Load environment variables
function loadEnv() {
  const envPath = path.join(process.cwd(), '.env.local');

  if (!fs.existsSync(envPath)) {
    return null;
  }

  const envFile = fs.readFileSync(envPath, 'utf-8');
  const env = {};

  envFile.split('\n').forEach(line => {
    line = line.trim();
    if (line && !line.startsWith('#')) {
      const [key, ...valueParts] = line.split('=');
      const value = valueParts.join('=').trim();
      if (key && value) {
        env[key] = value;
      }
    }
  });

  return env;
}

// Check environment file exists
function checkEnvFile() {
  log('\n📋 Checking environment configuration...', 'bright');

  const envPath = path.join(process.cwd(), '.env.local');

  if (fs.existsSync(envPath)) {
    success('.env.local file exists');
    return true;
  } else {
    error('.env.local file not found');
    info('Create it by running: cp .env.local.template .env.local');
    return false;
  }
}

// Check required environment variables
function checkEnvVariables(env) {
  log('\n🔑 Checking environment variables...', 'bright');

  const required = {
    'NEXT_PUBLIC_SUPABASE_URL': 'Supabase Project URL',
    'NEXT_PUBLIC_SUPABASE_ANON_KEY': 'Supabase Anonymous Key',
    'SUPABASE_SERVICE_ROLE_KEY': 'Supabase Service Role Key',
    'OPENAI_API_KEY': 'OpenAI API Key',
    'LUMA_API_KEY': 'Luma AI API Key',
    'ELEVENLABS_API_KEY': 'ElevenLabs API Key',
  };

  const optional = {
    'HAILUO_API_KEY': 'Hailuo AI Key (Backup video provider)',
    'ADMIN_API_KEY': 'Admin API Key',
    'ENGINE_URL': 'Backend Engine URL',
  };

  let allPresent = true;
  let optionalCount = 0;

  // Check required variables
  for (const [key, description] of Object.entries(required)) {
    if (env[key] && env[key].length > 10) {
      success(`${description} - Set`);
    } else {
      error(`${description} - Missing or invalid`);
      info(`  Set ${key} in .env.local`);
      allPresent = false;
    }
  }

  // Check optional variables
  log('\nOptional variables:', 'cyan');
  for (const [key, description] of Object.entries(optional)) {
    if (env[key] && env[key].length > 5) {
      success(`${description} - Set`);
      optionalCount++;
    } else {
      warning(`${description} - Not set`);
    }
  }

  if (allPresent) {
    success(`\nAll ${Object.keys(required).length} required variables are configured`);
  } else {
    error(`\nSome required variables are missing`);
  }

  return allPresent;
}

// Check Supabase connection
async function checkSupabaseConnection(env) {
  log('\n🗄️  Checking Supabase connection...', 'bright');

  const url = env['NEXT_PUBLIC_SUPABASE_URL'];
  const anonKey = env['NEXT_PUBLIC_SUPABASE_ANON_KEY'];

  if (!url || !anonKey) {
    error('Supabase credentials not configured');
    return false;
  }

  try {
    const response = await fetch(`${url}/rest/v1/`, {
      headers: {
        'apikey': anonKey,
        'Authorization': `Bearer ${anonKey}`
      }
    });

    if (response.ok || response.status === 404) {
      success('Supabase connection successful');

      // Check if tables exist
      const tablesResponse = await fetch(`${url}/rest/v1/waitlist_signups?limit=0`, {
        headers: {
          'apikey': anonKey,
          'Authorization': `Bearer ${anonKey}`,
          'Prefer': 'count=exact'
        }
      });

      if (tablesResponse.ok) {
        success('Database tables are accessible');
        return true;
      } else {
        warning('Tables may not be created yet');
        info('Run the SQL schema: See SUPABASE_SETUP.md');
        return true;
      }
    } else {
      error(`Supabase connection failed (${response.status})`);
      return false;
    }
  } catch (err) {
    error(`Supabase connection error: ${err.message}`);
    return false;
  }
}

// Check OpenAI API key
async function checkOpenAI(env) {
  log('\n🤖 Checking OpenAI API key...', 'bright');

  const apiKey = env['OPENAI_API_KEY'];

  if (!apiKey) {
    error('OpenAI API key not configured');
    return false;
  }

  try {
    const response = await fetch('https://api.openai.com/v1/models', {
      headers: {
        'Authorization': `Bearer ${apiKey}`
      }
    });

    if (response.ok) {
      const data = await response.json();
      const hasGPT4 = data.data.some(model => model.id.includes('gpt-4'));
      success('OpenAI API key is valid');
      if (hasGPT4) {
        success('GPT-4 access confirmed');
      } else {
        warning('GPT-4 access not detected (may need account verification)');
      }
      return true;
    } else {
      error(`OpenAI API key invalid (${response.status})`);
      if (response.status === 401) {
        info('Check your API key at: https://platform.openai.com/api-keys');
      } else if (response.status === 429) {
        warning('Rate limited or insufficient quota');
        info('Add billing at: https://platform.openai.com/account/billing');
      }
      return false;
    }
  } catch (err) {
    error(`OpenAI check failed: ${err.message}`);
    return false;
  }
}

// Check ElevenLabs API key
async function checkElevenLabs(env) {
  log('\n🎙️  Checking ElevenLabs API key...', 'bright');

  const apiKey = env['ELEVENLABS_API_KEY'];

  if (!apiKey) {
    error('ElevenLabs API key not configured');
    return false;
  }

  try {
    const response = await fetch('https://api.elevenlabs.io/v1/voices', {
      headers: {
        'xi-api-key': apiKey
      }
    });

    if (response.ok) {
      const data = await response.json();
      success('ElevenLabs API key is valid');
      success(`${data.voices?.length || 0} voices available`);
      return true;
    } else {
      error(`ElevenLabs API key invalid (${response.status})`);
      info('Check your API key at: https://elevenlabs.io/app/settings');
      return false;
    }
  } catch (err) {
    error(`ElevenLabs check failed: ${err.message}`);
    return false;
  }
}

// Check Luma AI API key
async function checkLumaAI(env) {
  log('\n🎬 Checking Luma AI API key...', 'bright');

  const apiKey = env['LUMA_API_KEY'];

  if (!apiKey) {
    error('Luma AI API key not configured');
    return false;
  }

  try {
    // Luma AI doesn't have a simple validation endpoint
    // We'll do a basic format check
    if (apiKey.length > 20) {
      warning('Luma AI API key format looks valid (cannot verify without test generation)');
      info('Test by generating a video in Creative Studio');
      return true;
    } else {
      error('Luma AI API key appears invalid (too short)');
      return false;
    }
  } catch (err) {
    error(`Luma AI check failed: ${err.message}`);
    return false;
  }
}

// Check backend connection
async function checkBackend(env) {
  log('\n⚙️  Checking backend engine...', 'bright');

  const engineUrl = env['ENGINE_URL'] || 'http://localhost:8000';

  try {
    const response = await fetch(`${engineUrl}/health`, {
      signal: AbortSignal.timeout(5000)
    });

    if (response.ok) {
      const data = await response.json();
      success('Backend engine is running');
      success(`Providers: ${JSON.stringify(data.providers || {})}`);
      return true;
    } else {
      error(`Backend returned error (${response.status})`);
      return false;
    }
  } catch (err) {
    error('Backend engine is not accessible');
    info('Start it with: cd engine && python server.py');
    return false;
  }
}

// Check Node.js and pnpm
function checkDependencies() {
  log('\n📦 Checking dependencies...', 'bright');

  // Check Node.js version
  const nodeVersion = process.version;
  const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);

  if (majorVersion >= 18) {
    success(`Node.js ${nodeVersion} (✓ >= 18)`);
  } else {
    error(`Node.js ${nodeVersion} (✗ Need >= 18)`);
  }

  // Check if node_modules exists
  if (fs.existsSync(path.join(process.cwd(), 'node_modules'))) {
    success('Dependencies installed (node_modules exists)');
  } else {
    error('Dependencies not installed');
    info('Run: pnpm install');
  }

  // Check Python (if available)
  try {
    const { execSync } = require('child_process');
    const pythonVersion = execSync('python3 --version', { encoding: 'utf-8' }).trim();
    success(`${pythonVersion}`);
  } catch {
    warning('Python 3 not found (needed for backend)');
  }
}

// Main validation function
async function main() {
  log('\n' + '='.repeat(60), 'bright');
  log('🚀 Relicon Setup Validation', 'bright');
  log('='.repeat(60) + '\n', 'bright');

  const results = {
    envFile: false,
    envVars: false,
    supabase: false,
    openai: false,
    elevenlabs: false,
    luma: false,
    backend: false,
  };

  // Check environment file
  results.envFile = checkEnvFile();

  if (!results.envFile) {
    log('\n' + '='.repeat(60), 'bright');
    error('❌ Setup incomplete: .env.local file not found');
    log('='.repeat(60) + '\n', 'bright');
    process.exit(1);
  }

  // Load environment variables
  const env = loadEnv();

  // Check environment variables
  results.envVars = checkEnvVariables(env);

  // Check dependencies
  checkDependencies();

  // Check services (if env vars are configured)
  if (results.envVars) {
    results.supabase = await checkSupabaseConnection(env);
    results.openai = await checkOpenAI(env);
    results.elevenlabs = await checkElevenLabs(env);
    results.luma = await checkLumaAI(env);
  }

  // Check backend
  results.backend = await checkBackend(env);

  // Summary
  log('\n' + '='.repeat(60), 'bright');
  log('📊 Validation Summary', 'bright');
  log('='.repeat(60), 'bright');

  const checks = [
    ['Environment file', results.envFile],
    ['Environment variables', results.envVars],
    ['Supabase connection', results.supabase],
    ['OpenAI API', results.openai],
    ['ElevenLabs API', results.elevenlabs],
    ['Luma AI API', results.luma],
    ['Backend engine', results.backend],
  ];

  let passCount = 0;
  checks.forEach(([name, passed]) => {
    if (passed) {
      success(name);
      passCount++;
    } else {
      error(name);
    }
  });

  log('\n' + '-'.repeat(60));
  log(`Result: ${passCount}/${checks.length} checks passed\n`, 'bright');

  if (passCount === checks.length) {
    success('✅ All checks passed! Your Relicon setup is complete.');
    log('\nNext steps:', 'bright');
    log('1. Start frontend: pnpm dev');
    log('2. Start backend: cd engine && python server.py');
    log('3. Visit: http://localhost:5000/dashboard/studio\n');
    process.exit(0);
  } else {
    error('❌ Some checks failed. Please fix the issues above.');
    log('\nRefer to these guides:', 'bright');
    log('- API Keys: See API_KEYS_GUIDE.md');
    log('- Supabase: See SUPABASE_SETUP.md');
    log('- General: See README.md\n');
    process.exit(1);
  }
}

// Run validation
main().catch(err => {
  error(`Validation failed: ${err.message}`);
  console.error(err);
  process.exit(1);
});
