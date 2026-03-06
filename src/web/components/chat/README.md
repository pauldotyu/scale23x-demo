# Chat UI Components

A well-structured chat interface for interacting with AI agents, built for Next.js with TypeScript and Tailwind CSS.

## Structure

```
components/chat/
├── ChatInterface.tsx    # Main chat container with header and layout
├── MessageList.tsx      # Scrollable message container
├── MessageBubble.tsx    # Individual message bubble
├── ChatInput.tsx        # Text input with send button
└── index.ts            # Barrel exports

hooks/
└── useChat.ts          # Custom hook for chat state and logic

types/
└── chat.ts             # TypeScript type definitions

app/api/chat/
└── route.ts            # API route handler for agent communication
```

## Features

✨ **Clean Architecture**

- Separation of concerns with modular components
- Custom React hook for state management
- TypeScript for type safety

💬 **User Experience**

- Real-time message updates
- Loading indicators with animated dots
- Error handling and display
- Auto-scroll to latest messages
- Keyboard shortcuts (Enter to send, Shift+Enter for new line)
- Responsive design with dark mode support

🎨 **Styling**

- Tailwind CSS for styling
- Smooth animations
- Accessible color contrast
- Mobile-friendly interface

## Usage

### Basic Implementation

The chat interface is already integrated into the main page (`app/page.tsx`):

```tsx
import { ChatInterface } from "@/components/chat";

export default function Home() {
  return (
    <div className="h-screen">
      <ChatInterface />
    </div>
  );
}
```

### Connecting to Your Backend

Update `app/api/chat/route.ts` to connect to your actual agent agent:

```typescript
const AGENT_API_URL = process.env.AGENT_API_URL || "http://localhost:8001";

// Replace the mock response with:
const response = await fetch(`${AGENT_API_URL}/chat`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    message,
    agent_id: agentId,
    history: history?.map((msg: any) => ({
      role: msg.role,
      content: msg.content,
    })),
  }),
});

const data = await response.json();
```

### Environment Variables

Add to your `.env.local`:

```
AGENT_API_URL=http://your-agent-url
```

## Components

### ChatInterface

The main container component that orchestrates the entire chat UI.

**Features:**

- Header with title and clear chat button
- Error message display
- Layout management

### MessageList

Handles the display of all messages with auto-scrolling.

**Features:**

- Empty state with helpful message
- Auto-scroll to bottom on new messages
- Loading indicator with animated dots

### MessageBubble

Displays individual messages with appropriate styling.

**Features:**

- Different styles for user vs assistant messages
- Agent name display for assistant messages
- Timestamp display
- Responsive text wrapping

### ChatInput

Text input component with send functionality.

**Features:**

- Multi-line support with Shift+Enter
- Enter to send (without Shift)
- Disabled state during loading
- Visual feedback

## Custom Hook

### useChat

Manages chat state and handles message sending logic.

**Returns:**

- `messages`: Array of chat messages
- `isLoading`: Boolean indicating if waiting for response
- `error`: Error message if any
- `sendMessage`: Function to send a message
- `clearMessages`: Function to clear all messages

**Example:**

```tsx
const { messages, isLoading, error, sendMessage, clearMessages } = useChat();
```

## Types

### Message

```typescript
interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  agentName?: string;
}
```

### ChatState

```typescript
interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}
```

## Customization

### Styling

All components use Tailwind CSS classes. Modify colors, spacing, and animations directly in the component files.

### Adding Features

**Multi-Agent Support:**

1. Add agent selector UI in `ChatInterface.tsx`
2. Pass selected `agentId` to `sendMessage` function
3. Update API route to route to specific agent

**File Attachments:**

1. Add file input in `ChatInput.tsx`
2. Update `Message` type to include attachments
3. Render attachments in `MessageBubble.tsx`

**Message History Persistence:**

1. Add localStorage/sessionStorage in `useChat` hook
2. Load messages on component mount
3. Save messages on state change

## Development

Run the development server:

```bash
npm run dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) to see the chat interface.

## Backend Integration

The current implementation includes a mock response. To connect to your Python agent agent:

1. Update the API route in `app/api/chat/route.ts`
2. Ensure your agent accepts POST requests with the format:
   ```json
   {
     "message": "user message",
     "agentId": "optional-agent-id",
     "history": [
       { "role": "user", "content": "previous message" },
       { "role": "assistant", "content": "previous response" }
     ]
   }
   ```
3. Expect responses in the format:
   ```json
   {
     "message": "agent response",
     "agentName": "Agent Name"
   }
   ```

## Best Practices

1. **Keep components small and focused** - Each component has a single responsibility
2. **Use TypeScript** - All props and states are properly typed
3. **Error handling** - Always handle API errors gracefully
4. **Accessibility** - Use semantic HTML and proper ARIA labels
5. **Performance** - Components are optimized to minimize re-renders

## Maintenance

- **Adding new message types**: Update the `Message` type in `types/chat.ts`
- **Changing layouts**: Modify `ChatInterface.tsx`
- **Updating styling**: Edit Tailwind classes in component files
- **API changes**: Update `app/api/chat/route.ts` and `useChat` hook
