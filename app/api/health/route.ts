import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Check database connection
    let dbStatus = 'unknown'
    let backendStatus = 'unknown'
    
    try {
      // Test Supabase connection
      const { createClient } = await import('@/lib/supabase-server')
      const supabase = createClient()
      const { error } = await supabase.from('users').select('count').limit(1)
      dbStatus = error ? 'error' : 'healthy'
    } catch (error) {
      dbStatus = 'error'
    }
    
    try {
      // Test backend connection
      const backendUrl = process.env.ENGINE_URL || 'http://localhost:8000'
      const response = await fetch(`${backendUrl}/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(5000) // 5 second timeout
      })
      backendStatus = response.ok ? 'healthy' : 'error'
    } catch (error) {
      backendStatus = 'error'
    }
    
    const overallStatus = dbStatus === 'healthy' && backendStatus === 'healthy' 
      ? 'healthy' 
      : 'degraded'
    
    const healthData = {
      status: overallStatus,
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version || '1.0.0',
      environment: process.env.NODE_ENV || 'development',
      services: {
        database: dbStatus,
        backend: backendStatus,
        frontend: 'healthy'
      },
      uptime: process.uptime(),
      memory: {
        used: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
        total: Math.round(process.memoryUsage().heapTotal / 1024 / 1024)
      }
    }
    
    const statusCode = overallStatus === 'healthy' ? 200 : 503
    
    return NextResponse.json(healthData, { 
      status: statusCode,
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    })
    
  } catch (error) {
    console.error('Health check failed:', error)
    
    return NextResponse.json(
      {
        status: 'error',
        timestamp: new Date().toISOString(),
        error: 'Health check failed',
        services: {
          database: 'unknown',
          backend: 'unknown',
          frontend: 'error'
        }
      },
      { status: 500 }
    )
  }
}
