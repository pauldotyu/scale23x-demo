# Frontend Coding Agent Instructions

You are an AI coding assistant specialized in Next.js, TypeScript, and React development for this AI chat web.

## Service Overview

Next.js web providing a retro-styled chat interface for AI agent interactions.

**Architecture:** Chat UI → Next.js API Route → API Gateway → Agent Service

## Core Technologies

- **Next.js 14+**: App Router, Server Components, API Routes
- **TypeScript**: Type-safe development
- **React Hooks**: State management with custom hooks
- **Tailwind CSS**: Utility-first styling with custom theme
- **Bun**: JavaScript runtime and package manager

## Project-Specific Patterns

### Custom Hook for Chat State Management

Centralize chat logic in `hooks/useChat.ts`:

```typescript
import { useState, useCallback } from "react";
import { Message, ChatState } from "@/types/chat";

export function useChat() {
  const [state, setState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    error: null,
  });

  const sendMessage = useCallback(
    async (content: string, agentId?: string) => {
      // Add user message immediately
      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content: content.trim(),
        timestamp: new Date(),
      };

      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, userMessage],
        isLoading: true,
        error: null,
      }));

      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: content,
            agentId,
            history: state.messages.slice(-10), // Send last 10 messages
          }),
        });

        if (!response.ok) throw new Error("Failed to get response");

        const data = await response.json();

        setState((prev) => ({
          ...prev,
          messages: [
            ...prev.messages,
            {
              id: crypto.randomUUID(),
              role: "assistant",
              content: data.message,
              timestamp: new Date(),
              agentName: data.agentName,
            },
          ],
          isLoading: false,
        }));
      } catch (error) {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: error instanceof Error ? error.message : "An error occurred",
        }));
      }
    },
    [state.messages]
  );

  const clearMessages = useCallback(() => {
    setState({ messages: [], isLoading: false, error: null });
  }, []);

  return { messages, isLoading, error, sendMessage, clearMessages };
}
```

**Key patterns:**

- Use `useCallback` for memoized functions to prevent re-renders
- Add user message immediately for optimistic UI
- Include conversation history (last 10 messages) for context
- Use `crypto.randomUUID()` for unique message IDs
- Handle errors gracefully and update state

### API Route Handler Pattern

Proxy requests to API Gateway in `app/api/chat/route.ts`:

```typescript
import { NextRequest } from "next/server";

const AGENT_SERVICE_URL =
  process.env.AGENT_SERVICE_URL || "http://api-gateway:8080";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, agentId, history, sessionId } = body;

    if (!message) {
      return new Response(JSON.stringify({ error: "Message is required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Forward to API Gateway with snake_case conversion
    const response = await fetch(`${AGENT_SERVICE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        agent_id: agentId,
        session_id: sessionId,
        history: history?.map((msg: HistoryMessage) => ({
          role: msg.role,
          content: msg.content,
        })),
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return new Response(
        JSON.stringify({ error: errorData.detail || "Failed to get response" }),
        {
          status: response.status,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    const data = await response.json();

    // Convert snake_case to camelCase for web
    return new Response(
      JSON.stringify({
        message: data.message,
        agentName: data.agent_name,
        sessionId: data.session_id,
      }),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Chat API error:", error);
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
```

**Key patterns:**

- Use `AGENT_SERVICE_URL` from environment variables
- Convert between camelCase (web) and snake_case (agent)
- Validate required fields before forwarding
- Catch JSON parsing errors with `.catch(() => ({}))`
- Always return proper status codes and error messages
- Log errors with `console.error` for server-side debugging

### Component Structure

Modular chat components in `components/chat/`:

```text
components/chat/
├── ChatInterface.tsx   # Main container with layout and state
├── MessageList.tsx     # Scrollable message container
├── MessageBubble.tsx   # Individual message component
├── ChatInput.tsx       # Input field with send button
└── index.ts           # Barrel exports
```

**Pattern:** Each component has a single responsibility:

```tsx
// ChatInterface.tsx - Container
export function ChatInterface() {
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat();

  return (
    <div className="flex flex-col h-screen">
      {/* Header with clear button */}
      {/* Error display */}
      <MessageList messages={messages} isLoading={isLoading} />
      <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
    </div>
  );
}

// MessageBubble.tsx - Presentational
export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-lg p-4 ${
          isUser ? "bg-blue-600" : "bg-gray-700"
        }`}
      >
        <p>{message.content}</p>
      </div>
    </div>
  );
}
```

### TypeScript Type Definitions

Define types in `types/chat.ts`:

```typescript
export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  agentName?: string;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}
```

**Pattern:** Use interfaces for object shapes, union types for role/status enums.

### Styling with Tailwind CSS

The project uses a custom retro theme (see `THEMING.md`):

```tsx
// Use custom CSS variables defined in globals.css
<h1 className="text-2xl font-bold font-[family-name:var(--font-press-start)] neon-glow-green">
  SCALE23X
</h1>

// Responsive spacing and layouts
<div className="max-w-4xl mx-auto px-4 py-4">
  {/* Content */}
</div>

// Loading states with animations
<div className="animate-fade-in">
  <span className="loading-dot">•</span>
</div>
```

**Key patterns:**

- Use custom CSS variables for theme colors (see `globals.css`)
- Responsive design with `max-w-*` and `mx-auto`
- Custom animations defined in Tailwind config
- Retro styling with `Press Start 2P` font and neon effects

## Environment Variables

Required configuration (`.env.local`):

```bash
# API Gateway URL (used by API route)
AGENT_SERVICE_URL=http://localhost:8080

# For Docker deployment
AGENT_SERVICE_URL=http://api-gateway:8080
```

## Development Workflow

```bash
# Install dependencies
bun install

# Run dev server
bun run dev

# Build for production
bun run build

# Run production server
bun start

# Type checking
bun run type-check

# Linting
bun run lint
```

## Testing

```bash
# Test in browser
open http://localhost:3000

# Test API route directly
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

## Best Practices

- **Use "use client" directive** for components with hooks/state
- **Memoize callbacks** with `useCallback` to prevent re-renders
- **Handle loading states** for better UX (show spinners, disable inputs)
- **Optimistic UI updates** - add user messages immediately
- **Error boundaries** - catch and display errors gracefully
- **Accessibility** - use semantic HTML, ARIA labels
- **Type safety** - define interfaces for all data structures
- **CSS organization** - use Tailwind utilities, extract complex styles to globals.css
- **Component composition** - keep components small and focused

## Common Patterns

### Conditional Rendering

```tsx
{
  error && (
    <div className="error-container">
      <p>{error}</p>
    </div>
  );
}

{
  messages.length > 0 && <button onClick={clearMessages}>Clear</button>;
}
```

### Array Mapping with Keys

```tsx
{
  messages.map((msg) => <MessageBubble key={msg.id} message={msg} />);
}
```

### Event Handlers

```tsx
const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault();
  if (input.trim()) {
    sendMessage(input);
    setInput("");
  }
};

// Keyboard shortcuts
const handleKeyDown = (e: React.KeyboardEvent) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSubmit(e);
  }
};
```

## References

- [Next.js Documentation](https://nextjs.org/docs)
- [React Hooks](https://react.dev/reference/react/hooks)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- Project theming: See `THEMING.md` for custom styles and design system
