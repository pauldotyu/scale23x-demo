import { NextRequest } from 'next/server';

// Agent Service URL - connects directly to the AI agent service
const AGENT_SERVICE_URL = process.env.AGENT_SERVICE_URL || 'http://agent:8001';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, agentId, sessionId } = body;

    if (!message) {
      return new Response(
        JSON.stringify({ error: 'Message is required' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Forward request directly to Agent Service
    const response = await fetch(`${AGENT_SERVICE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        agent_id: agentId,
        session_id: sessionId || null,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('Agent API error:', response.status, errorData);
      return new Response(
        JSON.stringify({ error: errorData.detail || 'Failed to get response from agent' }),
        { status: response.status, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const data = await response.json();
    return new Response(
      JSON.stringify({
        message: data.message,
        agentName: data.agent_name,
        sessionId: data.session_id,
      }),
      { headers: { 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('Chat API error:', error);
    return new Response(
      JSON.stringify({ error: 'Failed to process message' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}
