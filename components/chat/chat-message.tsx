"use client"

import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Card } from '@/components/ui/card';
import { Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { cn } from '@/lib/utils';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={cn(
      "flex items-start space-x-3 mb-6",
      isUser ? "flex-row-reverse space-x-reverse" : ""
    )}>
      <Avatar className="h-8 w-8 shrink-0">
        <AvatarFallback className={cn(
          "text-xs font-medium",
          isUser 
            ? "bg-primary text-primary-foreground" 
            : "bg-muted text-muted-foreground"
        )}>
          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>

      <Card className={cn(
        "max-w-[80%] p-4 shadow-sm",
        isUser 
          ? "bg-primary text-primary-foreground ml-auto" 
          : "bg-muted/50"
      )}>
        <div className={cn(
          "prose prose-sm max-w-none",
          isUser 
            ? "prose-invert" 
            : "prose-neutral dark:prose-invert"
        )}>
          <ReactMarkdown
            components={{
              p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
              ul: ({ children }) => <ul className="mb-2 last:mb-0 pl-4">{children}</ul>,
              ol: ({ children }) => <ol className="mb-2 last:mb-0 pl-4">{children}</ol>,
              li: ({ children }) => <li className="mb-1">{children}</li>,
              code: ({ children, className }) => {
                const isInline = !className;
                return isInline ? (
                  <code className={cn(
                    "px-1.5 py-0.5 rounded text-xs font-mono",
                    isUser 
                      ? "bg-primary-foreground/20" 
                      : "bg-muted"
                  )}>
                    {children}
                  </code>
                ) : (
                  <pre className={cn(
                    "p-3 rounded-lg text-xs font-mono overflow-x-auto",
                    isUser 
                      ? "bg-primary-foreground/20" 
                      : "bg-muted"
                  )}>
                    <code>{children}</code>
                  </pre>
                );
              },
              h1: ({ children }) => <h1 className="text-lg font-semibold mb-2">{children}</h1>,
              h2: ({ children }) => <h2 className="text-base font-semibold mb-2">{children}</h2>,
              h3: ({ children }) => <h3 className="text-sm font-semibold mb-2">{children}</h3>,
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>
      </Card>
    </div>
  );
}