"""
AI Agent Service

This service handles the actual AI interactions using the agent-framework.
It exposes an API endpoint that receives chat messages and returns AI-generated responses.
It also manages session state using Redis for conversation history persistence.
"""

import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from agent_framework import Agent, AgentSession
from agent_framework.observability import configure_otel_providers
from agent_framework.redis import RedisHistoryProvider
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from kaito_client import KAITOChatClient
import redis.asyncio as redis
import json

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv(
    "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"
)
ENABLE_INSTRUMENTATION = os.getenv("ENABLE_INSTRUMENTATION", "false").lower() == "true"
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_CHAT_MODEL_ID = os.getenv("OPENAI_CHAT_MODEL_ID", "gemma-3-27b-instruct")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "none")
RAG_INDEX_NAME = os.getenv("RAG_INDEX_NAME")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_SESSION_TTL = int(os.getenv("REDIS_SESSION_TTL", "3600"))  # 1 hour default
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Setup observability first to instrument logging
configure_otel_providers(enable_sensitive_data=True)


def create_redis_history_provider():
    """Create a Redis history provider for persisting chat messages."""
    return RedisHistoryProvider(
        source_id="redis-history",
        redis_url=REDIS_URL,
    )


class ChatMessage(BaseModel):
    """Individual chat message"""

    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    """Request body for chat endpoint"""

    message: str = Field(..., min_length=1)
    agent_id: str | None = None
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Response body for chat endpoint"""

    message: str
    agent_name: str
    session_id: str


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    service: str


# Application state
class AppState:
    """Shared application state"""

    agent: Agent | None = None
    # Map session_id -> AgentSession for per-user conversation isolation
    sessions: dict[str, AgentSession] = {}


app_state = AppState()


# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown logic"""

    print(f"OPENAI_BASE_URL: {OPENAI_BASE_URL}")
    print(f"OPENAI_CHAT_MODEL_ID: {OPENAI_CHAT_MODEL_ID}")
    if RAG_INDEX_NAME:
        print(f"RAG_INDEX_NAME: {RAG_INDEX_NAME}")

    try:
        app_state.agent = Agent(
            client=KAITOChatClient(),
            name="AI Agent",
            instructions="You are a helpful assistant and expert in Linux and free open-source software (FOSS). You have all the session information available to you including title, descrtiption, time, and location and are able to answer any question about FOSS projects and give users timely information about the SCALE23X schedule. When you answer a question about the SCALE23X schedule, ALWAYS cite the relevant sessions by their titles, location, date, time, speakers, and ALWAYS include the URL to the session so that the user can get more details from the official SCALE23X event website. If you are listing multiple events, ALWAYS make sure they are ordered in chronological order.",
            context_providers=[create_redis_history_provider()],
            default_options={"max_tokens": 2048},
        )
        await app_state.agent.__aenter__()
    except Exception as e:
        print(f"Failed to initialize Agent: {e}")
        raise

    yield

    # Shutdown
    print("Shutting down AI Agent Service")
    if app_state.agent:
        await app_state.agent.__aexit__(None, None, None)
        print("Agent closed")


# Create FastAPI app
app = FastAPI(
    title="AI Agent Service",
    version="0.1.0",
    description="AI Agent Service using agent-framework",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", service="agent-service")


@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Retrieve chat history for a given session from Redis

    Returns:
        List of chat messages in chronological order
    """

    redis_client = None
    try:
        # Connect directly to Redis to retrieve the stored messages
        redis_client = redis.from_url(REDIS_URL, decode_responses=False)

        # The agent_framework stores messages with keys like "chat_messages:thread_{thread_id}"
        # We need to get all messages for this thread
        messages_key = f"chat_messages:{session_id}"

        # Get all messages from the Redis list
        # Type ignore because redis.asyncio types may not be perfect
        raw_messages: list[bytes] = await redis_client.lrange(messages_key, 0, -1)  # type: ignore

        print(
            f"Retrieved {len(raw_messages)} raw messages from Redis for session: {session_id}"
        )
        print(f"Redis key: {messages_key}")

        # Parse and convert messages to our API format
        history = []
        for raw_msg in raw_messages:
            try:
                msg_data = json.loads(raw_msg)

                # Extract role - handle nested structure {"type":"role","value":"user"}
                role = "user"
                if "role" in msg_data:
                    role_data = msg_data["role"]
                    if isinstance(role_data, dict) and "value" in role_data:
                        role = role_data["value"]
                    elif isinstance(role_data, str):
                        role = role_data

                # Extract content from the message
                content = ""
                if "contents" in msg_data and msg_data["contents"]:
                    for content_item in msg_data["contents"]:
                        if "text" in content_item:
                            content = content_item["text"]
                            break
                elif "content" in msg_data:
                    content = msg_data["content"]

                # Extract agent name if present
                agent_name = msg_data.get("author_name")

                message = {
                    "role": role,
                    "content": content,
                    "timestamp": msg_data.get("created_at"),
                }

                # Only add agent_name if it exists
                if agent_name:
                    message["agent_name"] = agent_name

                history.append(message)
            except Exception as parse_error:
                print(f"Error parsing message: {parse_error}")
                continue

        return {"messages": history, "session_id": session_id}

    except Exception as e:
        print(f"Error retrieving chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")

    finally:
        if redis_client:
            await redis_client.aclose()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint that processes messages using the AI agent (non-streaming)

    If session_id is None, creates a new thread and session.
    If session_id is provided, retrieves or recreates the thread for that session.

    The session_id is the agent framework's native thread ID.
    """
    if not app_state.agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        # Get or create session
        if request.session_id:
            # Retrieve or recreate session by ID
            session_id = request.session_id
            if session_id not in app_state.sessions:
                # Session doesn't exist in memory
                # Recreate it (Redis history provider loads messages by session_id)
                session = AgentSession(session_id=session_id)
                app_state.sessions[session_id] = session
                print(f"Recreated session from Redis for session: {session_id}")
            else:
                session = app_state.sessions[session_id]
        else:
            # Create a new session
            session = AgentSession()
            session_id = session.session_id
            app_state.sessions[session_id] = session
            print(f"Created new session: {session_id}")

        # If rag index name is provided, include it in options
        if RAG_INDEX_NAME:
            result = await app_state.agent.run(
                messages=request.message,
                options={
                    "extra_body": {
                        "index_name": RAG_INDEX_NAME,
                        "model": OPENAI_CHAT_MODEL_ID,
                    }
                },
                session=session,
            )
        else:
            result = await app_state.agent.run(
                messages=request.message,
                session=session,
            )

        return ChatResponse(
            message=result.text, agent_name="AI Agent", session_id=session_id
        )

    except Exception as e:
        print(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
