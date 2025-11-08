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

console.log('🔧 Debug info:')
console.log(`   Supabase URL: ${env.NEXT_PUBLIC_SUPABASE_URL}`)
console.log(`   Service Key: ${env.SUPABASE_SERVICE_ROLE_KEY ? 'Present' : 'Missing'}`)

const supabase = createClient(
  env.NEXT_PUBLIC_SUPABASE_URL,
  env.SUPABASE_SERVICE_ROLE_KEY
)

async function createUser(email, password, userData = {}) {
  try {
    console.log(`🔄 Creating user: ${email}`)
    
    const { data, error } = await supabase.auth.admin.createUser({
      email,
      password,
      email_confirm: true,
      user_metadata: {
        name: userData.name || email.split('@')[0],
        company: userData.company || '',
        role: userData.role || 'user'
      }
    })

    if (error) {
      console.error('❌ Supabase error:', error)
      throw error
    }

    console.log('✅ User created successfully:')
    console.log(`   Email: ${email}`)
    console.log(`   Password: ${password}`)
    console.log(`   User ID: ${data.user.id}`)
    console.log(`   Created at: ${data.user.created_at}`)
    
    return data.user
  } catch (error) {
    console.error('❌ Error creating user:', error.message)
    if (error.details) console.error('   Details:', error.details)
    throw error
  }
}

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2)
  
  if (args.length < 2) {
    console.log('Usage: node scripts/create-user.js <email> <password> [name] [company]')
    console.log('Example: node scripts/create-user.js user@company.com password123 "John Doe" "Acme Corp"')
    process.exit(1)
  }

  const [email, password, name, company] = args
  
  createUser(email, password, { name, company })
    .then(() => process.exit(0))
    .catch(() => process.exit(1))
}

module.exports = { createUser }
