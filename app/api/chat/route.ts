import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const SYSTEM_PROMPT = `You are Relicon AI, an expert advertising and analytics assistant specializing in social media marketing, video ads, and performance optimization.

Your primary role is to help users:
1. **Understand their ad performance metrics** (CTR, ROAS, conversions, reach, impressions, engagement)
2. **Analyze campaign performance** and identify what's working or not working
3. **Provide actionable recommendations** to improve ROI and reduce costs
4. **Answer questions about advertising concepts** (CTR, ROAS, CPM, CPC, conversion tracking)
5. **Suggest creative strategies** for video ads on Instagram, Facebook, and TikTok
6. **Help with campaign planning** and budget allocation

Always be helpful, concise, and provide actionable insights. Keep responses under 200 words.`;

export async function POST(request: NextRequest) {
  try {
    if (!process.env.OPENAI_API_KEY) {
      return NextResponse.json(
        { error: 'OpenAI API key not configured' },
        { status: 500 }
      );
    }

    const { messages, message } = await request.json();
    
    // Handle both message formats
    const userMessage = message || (messages && messages[messages.length - 1]?.content);
    
    if (!userMessage) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    const completion = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: userMessage }
      ],
      max_tokens: 300,
      temperature: 0.7,
    });

    const response = completion.choices[0]?.message?.content || 'I apologize, but I could not generate a response.';

    return NextResponse.json({ message: response });

  } catch (error: any) {
    console.error('Chat API error:', error);
    
    return NextResponse.json(
      { error: 'Chat service temporarily unavailable. Please try again.' },
      { status: 500 }
    );
  }
}
