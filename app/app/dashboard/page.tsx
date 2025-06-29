"use client"

import { AppLayout } from '@/components/layouts/app-layout';
import { ChatInterface } from '@/components/chat/chat-interface';

export default function DashboardPage() {
  return (
    <AppLayout>
      <div className="h-full -m-6">
        <ChatInterface />
      </div>
    </AppLayout>
  );
}