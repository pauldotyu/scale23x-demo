import { NextRequest } from 'next/server';

// Agent Service URL - connects directly to the AI agent service
const AGENT_SERVICE_URL = process.env.AGENT_SERVICE_URL || 'http://agent:8001';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ sessionId: string }> }
) {
  try {
    const { sessionId } = await params;

    if (!sessionId) {
      return new Response(
        JSON.stringify({ error: 'Session ID is required' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Forward request to Agent Service to retrieve chat history
    const response = await fetch(`${AGENT_SERVICE_URL}/chat/history/${sessionId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('Agent API error:', response.status, errorData);
      return new Response(
        JSON.stringify({ error: errorData.detail || 'Failed to retrieve chat history' }),
        { status: response.status, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const data = await response.json();
    
    // Convert messages to frontend format
    interface HistoryMessage {
      role: string;
      content: string;
      timestamp?: string;
      agent_name?: string;
    }
    
    const messages = (data.messages as HistoryMessage[]).map((msg) => ({
      role: msg.role,
      content: msg.content,
      timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date(),
      ...(msg.agent_name && { agentName: msg.agent_name }),
    }));

    return new Response(
      JSON.stringify({
        messages,
        sessionId: data.session_id,
      }),
      { headers: { 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('Chat history API error:', error);
    return new Response(
      JSON.stringify({ error: 'Failed to retrieve chat history' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}
