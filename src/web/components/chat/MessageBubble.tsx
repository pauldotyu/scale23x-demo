"use client";

import { Message } from "@/types/chat";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex ${
        isUser ? "justify-end" : "justify-start"
      } mb-4 animate-fade-in`}
    >
      <div
        className={`max-w-[80%] md:max-w-[70%] rounded-2xl px-4 py-3 border-2 ${
          isUser
            ? "message-bubble-user neon-shadow-pink"
            : "message-bubble-agent neon-shadow-cyan"
        }`}
      >
        {!isUser && message.agentName && (
          <div className="agent-name text-xs font-bold mb-2 font-[family-name:var(--font-press-start)] tracking-wider neon-glow-yellow">
            {message.agentName.toUpperCase()}
          </div>
        )}
        <div
          className={`text-base leading-relaxed markdown-content font-[family-name:var(--font-atkinson)] ${
            isUser ? "text-white" : "text-gray-100"
          }`}
        >
          {isUser ? (
            // User messages: plain text
            <div className="whitespace-pre-wrap break-words">
              {message.content}
            </div>
          ) : (
            // Assistant messages: render markdown
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
              components={{
                // Custom styling for markdown elements
                p: ({ children }) => (
                  <p className="mb-2 last:mb-0">{children}</p>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc list-inside mb-2 space-y-1">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal list-inside mb-2 space-y-1">
                    {children}
                  </ol>
                ),
                li: ({ children }) => <li className="ml-2">{children}</li>,
                code: ({ className, children, ...props }) => {
                  const match = /language-(\w+)/.exec(className || "");
                  return match ? (
                    // Code block
                    <code
                      className={`${className} block bg-black text-gray-100 p-3 rounded-lg my-2 overflow-x-auto text-xs border border-gray-700`}
                      {...props}
                    >
                      {children}
                    </code>
                  ) : (
                    // Inline code
                    <code
                      className="inline-code px-1.5 py-0.5 rounded text-xs border neon-shadow-pink-subtle"
                      {...props}
                    >
                      {children}
                    </code>
                  );
                },
                pre: ({ children }) => <pre className="my-2">{children}</pre>,
                h1: ({ children }) => (
                  <h1 className="text-xl font-bold mb-2 mt-3 first:mt-0">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-lg font-bold mb-2 mt-2 first:mt-0">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-base font-bold mb-1 mt-2 first:mt-0">
                    {children}
                  </h3>
                ),
                a: ({ children, href }) => (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:text-blue-600 underline"
                  >
                    {children}
                  </a>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-gray-400 pl-3 italic my-2">
                    {children}
                  </blockquote>
                ),
                table: ({ children }) => (
                  <div className="overflow-x-auto my-2">
                    <table className="min-w-full border-collapse border border-gray-600">
                      {children}
                    </table>
                  </div>
                ),
                th: ({ children }) => (
                  <th className="border border-gray-600 px-3 py-1 bg-gray-700 font-semibold">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="border border-gray-600 px-3 py-1">
                    {children}
                  </td>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>
        {/* Only show timestamp if message has content */}
        {message.content && (
          <div
            className={`text-xs mt-1 ${
              isUser ? "text-blue-100" : "text-gray-500 dark:text-gray-400"
            }`}
          >
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
        )}
      </div>
    </div>
  );
}
