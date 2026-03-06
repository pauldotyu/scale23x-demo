"use client";

import { useChat } from "@/hooks/useChat";
import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";

interface ChatInterfaceProps {
  sessionId?: string;
}

export function ChatInterface({ sessionId }: ChatInterfaceProps) {
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat(sessionId);

  return (
    <div className="relative flex flex-col h-screen max-h-screen bg-gradient-to-b from-[var(--purple-dark)] via-[var(--gray-darker)] to-[var(--background)]">
      {/* Retro city background */}
      <div className="absolute inset-0 bg-[url('/images/city-bg.png')] bg-cover opacity-30 pixelize"></div>

      {/* Content overlay */}
      <div className="relative z-10 flex flex-col h-full">
        {/* Header - Deep black with neon accents */}
        <div className="chat-header border-b-2 backdrop-blur-sm px-4 py-4 shadow-lg shadow-[var(--neon-pink)]/30 header-border">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <div>
              <h1 className="chat-title text-2xl font-bold drop-shadow-lg font-[family-name:var(--font-press-start)] tracking-wider neon-glow-green">
                SCALE23X GAMEPLAN
              </h1>
              <p className="chat-subtitle text-sm drop-shadow-md mt-3 font-[family-name:var(--font-press-start)] tracking-wide neon-glow-pink">
                POWERED BY KAITO
              </p>
            </div>
            {messages.length > 0 && (
              <button
                onClick={clearMessages}
                className="clear-button text-xs font-bold px-4 py-3 border-2 rounded-md transition-all shadow-lg hover:shadow-xl hover:shadow-[var(--neon-yellow)]/50 font-[family-name:var(--font-press-start)] tracking-wider neon-shadow-yellow"
              >
                CLEAR
              </button>
            )}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-container border-2 rounded-md p-4 mx-4 mt-4 max-w-4xl mx-auto animate-fade-in">
            <div className="flex items-center gap-3">
              <div className="flex-shrink-0">
                <span className="error-icon">⚠️</span>
              </div>
              <div className="flex-1">
                <p className="error-text text-sm font-[family-name:var(--font-press-start)] tracking-wide uppercase">
                  {error}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Messages */}
        <MessageList messages={messages} isLoading={isLoading} />

        {/* Input */}
        <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}
