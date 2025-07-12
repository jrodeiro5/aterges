"use client"

import { ChatLayout } from '@/components/layouts/chat-layout';
import { ChatInterface } from '@/components/chat/chat-interface';

export default function DashboardPage() {
  return (
    <ChatLayout>
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="border-b p-4 bg-background/95">
          <h1 className="text-xl font-semibold">Dashboard</h1>
          <p className="text-muted-foreground text-sm">Chat con IA y resumen de actividad</p>
        </div>

        {/* Chat Interface */}
        <div className="flex-1 overflow-hidden">
          <ChatInterface />
        </div>
      </div>
    </ChatLayout>
  );
}
