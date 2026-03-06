import { useState, useCallback, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Message, ChatState } from '@/types/chat';

const MESSAGES_STORAGE_PREFIX = 'chat_messages_';

const generateUUID = (): string => {
  if (typeof window !== 'undefined' && window.crypto?.randomUUID) {
    return window.crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

const getStorageKey = (sessionId: string | null) => 
  `${MESSAGES_STORAGE_PREFIX}${sessionId || 'new'}`;

const saveMessages = (sessionId: string | null, messages: Message[]) => {
  if (!messages.length) return;
  try {
    sessionStorage.setItem(getStorageKey(sessionId), JSON.stringify(messages));
  } catch (error) {
    console.warn('Failed to persist messages:', error);
  }
};

export function useChat(initialSessionId?: string) {
  const router = useRouter();
  const pendingRedirectRef = useRef(false);
  const [sessionId, setSessionId] = useState<string | null>(
    initialSessionId || null
  );
  const [state, setState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    error: null,
  });

  // Restore messages on session change
  useEffect(() => {
    if (sessionId === null) {
      setState({ messages: [], isLoading: false, error: null });
      sessionStorage.removeItem(getStorageKey(null));
      return;
    }

    // First, try to restore from sessionStorage
    const storedMessages = sessionStorage.getItem(getStorageKey(sessionId));
    if (storedMessages) {
      try {
        setState(prev => ({ ...prev, messages: JSON.parse(storedMessages) }));
        return; // Skip fetching from backend if we have local data
      } catch (error) {
        console.error('Failed to restore messages from sessionStorage:', error);
      }
    }

    // If not in sessionStorage, fetch from backend
    const fetchChatHistory = async () => {
      try {
        setState(prev => ({ ...prev, isLoading: true }));
        console.log('[useChat] Fetching chat history for session:', sessionId);
        const response = await fetch(`/api/chat/history/${sessionId}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch chat history');
        }
        
        const data = await response.json();
        console.log('[useChat] Received chat history data:', data);
        
        // Convert the history messages to our Message format
        const historyMessages: Message[] = data.messages.map((msg: { role: string; content: string; timestamp: string; agentName?: string }) => ({
          id: generateUUID(),
          role: msg.role as 'user' | 'assistant' | 'system',
          content: msg.content,
          timestamp: new Date(msg.timestamp),
          ...(msg.agentName && { agentName: msg.agentName }),
        }));
        
        console.log('[useChat] Converted to history messages:', historyMessages);
        setState(prev => ({ ...prev, messages: historyMessages, isLoading: false }));
        
        // Save to sessionStorage for future use
        saveMessages(sessionId, historyMessages);
      } catch (error) {
        console.error('Failed to fetch chat history:', error);
        setState(prev => ({ 
          ...prev, 
          isLoading: false,
          error: 'Failed to load chat history'
        }));
      }
    };

    fetchChatHistory();
  }, [sessionId]);

  // Persist messages on change
  useEffect(() => {
    if (!pendingRedirectRef.current) {
      saveMessages(sessionId, state.messages);
    }
  }, [state.messages, sessionId]);

  const sendMessage = useCallback(
    async (content: string, agentId?: string) => {
      const trimmedContent = content.trim();
      if (!trimmedContent) return;

      // Add user message
      const userMessage: Message = {
        id: generateUUID(),
        role: 'user',
        content: trimmedContent,
        timestamp: new Date(),
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, userMessage],
        isLoading: true,
        error: null,
      }));

      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: trimmedContent, agentId, sessionId }),
        });

        if (!response.ok) throw new Error('Failed to get response from agent');
        const data = await response.json();

        const assistantMessage: Message = {
          id: generateUUID(),
          role: 'assistant',
          content: data.message,
          timestamp: new Date(),
          agentName: data.agentName,
        };

        setState(prev => {
          const updatedMessages = [...prev.messages, assistantMessage];
          
          // Handle new session - save messages before redirect
          if (data.sessionId && data.sessionId !== sessionId) {
            saveMessages(data.sessionId, updatedMessages);
            pendingRedirectRef.current = true;
            // Use setTimeout to ensure state update completes before navigation
            setTimeout(() => {
              setSessionId(data.sessionId);
              router.push(`/${data.sessionId}`);
            }, 0);
          }
          
          return { ...prev, messages: updatedMessages, isLoading: false };
        });
      } catch (error) {
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: error instanceof Error ? error.message : 'An error occurred',
        }));
      }
    },
    [sessionId, router]
  );

  const clearMessages = useCallback(() => {
    setState({ messages: [], isLoading: false, error: null });
    setSessionId(null);
    pendingRedirectRef.current = false;
    router.push('/');
  }, [router]);

  return { 
    messages: state.messages, 
    isLoading: state.isLoading, 
    error: state.error, 
    sendMessage, 
    clearMessages, 
    sessionId, 
    setSessionId 
  };
}
