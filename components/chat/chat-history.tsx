"use client"

import { useEffect, useRef } from 'react';
import { ChatMessage } from './chat-message';
import { ScrollArea } from '@/components/ui/scroll-area';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

interface ChatHistoryProps {
  messages: Message[];
}

export function ChatHistory({ messages }: ChatHistoryProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Scroll to bottom when new messages are added
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center space-y-4 max-w-md">
          <div className="w-16 h-16 mx-auto bg-primary/10 rounded-full flex items-center justify-center">
            <svg
              className="w-8 h-8 text-primary"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
          </div>
          <div className="space-y-2">
            <h3 className="text-lg font-semibold">¡Hola! Soy tu Asistente de IA</h3>
            <p className="text-muted-foreground">
              Pregúntame cualquier cosa sobre tus datos, procesos o necesidades empresariales. 
              Estoy aquí para ayudarte a optimizar tu negocio.
            </p>
          </div>
          <div className="flex flex-wrap gap-2 justify-center">
            <div className="px-3 py-1 bg-muted rounded-full text-xs text-muted-foreground">
              Análisis de datos
            </div>
            <div className="px-3 py-1 bg-muted rounded-full text-xs text-muted-foreground">
              Automatización
            </div>
            <div className="px-3 py-1 bg-muted rounded-full text-xs text-muted-foreground">
              Estrategias de marketing
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1 px-4" ref={scrollAreaRef}>
      <div className="max-w-4xl mx-auto py-6">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}