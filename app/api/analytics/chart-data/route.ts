import { NextResponse } from 'next/server'
import { supabaseServer } from '@/lib/supabase-server'

export async function GET() {
  try {
    // Get daily analytics for the last 7 days
    const { data, error } = await supabaseServer
      .from('post_analytics')
      .select('metrics_date, roas, conversions, spend')
      .gte('metrics_date', new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0])
      .order('metrics_date', { ascending: true })

    if (error) {
      console.error('Error fetching chart data:', error)
      return NextResponse.json({ error: 'Failed to fetch chart data' }, { status: 500 })
    }

    // Group by date and sum metrics
    const chartData = data?.reduce((acc: any[], row) => {
      const existingDate = acc.find(item => item.date === row.metrics_date)
      if (existingDate) {
        existingDate.roas = (existingDate.roas + (row.roas || 0)) / 2 // Average ROAS
        existingDate.conversions += row.conversions || 0
        existingDate.spend += row.spend || 0
      } else {
        acc.push({
          date: new Date(row.metrics_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          roas: row.roas || 0,
          conversions: row.conversions || 0,
          spend: row.spend || 0
        })
      }
      return acc
    }, []) || []

    return NextResponse.json(chartData)
  } catch (error) {
    console.error('Error in chart data API:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
