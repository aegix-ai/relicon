#!/usr/bin/env node

const { createClient } = require('@supabase/supabase-js')
const fs = require('fs')
const path = require('path')

// Read .env.local file
const envPath = path.join(__dirname, '..', '.env.local')
const envContent = fs.readFileSync(envPath, 'utf8')

const env = {}
envContent.split('\n').forEach(line => {
  const [key, ...valueParts] = line.split('=')
  if (key && valueParts.length) {
    env[key.trim()] = valueParts.join('=').trim()
  }
})

const supabase = createClient(
  env.NEXT_PUBLIC_SUPABASE_URL,
  env.SUPABASE_SERVICE_ROLE_KEY
)

async function listUsers() {
  try {
    const { data, error } = await supabase.auth.admin.listUsers()

    if (error) throw error

    console.log(`📋 Found ${data.users.length} users:`)
    data.users.forEach(user => {
      console.log(`   • ${user.email} (ID: ${user.id})`)
      console.log(`     Created: ${user.created_at}`)
      console.log(`     Name: ${user.user_metadata?.name || 'Not set'}`)
      console.log(`     Company: ${user.user_metadata?.company || 'Not set'}`)
      console.log('')
    })
    
    return data.users
  } catch (error) {
    console.error('❌ Error listing users:', error.message)
    throw error
  }
}

listUsers()
  .then(() => process.exit(0))
  .catch(() => process.exit(1))
