// components/layouts/chat-layout-example.tsx
'use client';

/**
 * Example of how to use the new ChatLayout
 * This can be copied to any page that needs the new chat interface
 */

import React from 'react';
import { ChatLayout } from './chat-layout';
import { ChatInterface } from '../chat/chat-interface';

// Example: Dashboard page with new chat layout
export function DashboardWithChatLayout() {
  return (
    <ChatLayout>
      <div className="flex-1 flex flex-col">
        {/* Chat Header - Optional, shows current page context */}
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

// Example: Simple page with chat layout
export function SimplePageWithChatLayout() {
  return (
    <ChatLayout>
      <div className="flex-1 flex flex-col">
        {/* Page Content */}
        <div className="flex-1 p-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="text-2xl font-bold mb-4">Your Page Content</h1>
            <p className="text-muted-foreground">
              This page uses the new chat layout with sidebar for conversation history.
            </p>
          </div>
        </div>
      </div>
    </ChatLayout>
  );
}

// Example: How to replace existing AppLayout usage
export function HowToMigrate() {
  /*
  OLD WAY (app-layout.tsx):
  
  import { AppLayout } from '@/components/layouts/app-layout';
  
  export default function DashboardPage() {
    return (
      <AppLayout>
        <ChatInterface />
      </AppLayout>
    );
  }

  NEW WAY (chat-layout.tsx):
  
  import { ChatLayout } from '@/components/layouts/chat-layout';
  import { ChatInterface } from '@/components/chat/chat-interface';
  
  export default function DashboardPage() {
    return (
      <ChatLayout>
        <div className="flex-1 overflow-hidden">
          <ChatInterface />
        </div>
      </ChatLayout>
    );
  }

  OR using the wrapper:

  import { withChatLayout } from '@/components/layouts/chat-layout';
  import { ChatInterface } from '@/components/chat/chat-interface';
  
  function DashboardPage() {
    return (
      <div className="flex-1 overflow-hidden">
        <ChatInterface />
      </div>
    );
  }
  
  export default withChatLayout(DashboardPage);
  */

  return null;
}

/* 
=== IMPLEMENTATION INSTRUCTIONS ===

1. To use the new chat layout in any page, replace:
   - AppLayout with ChatLayout
   - Wrap your content appropriately

2. The new layout provides:
   - ✅ Header with navigation (Dashboard, Agentes, Integraciones, Configuración)
   - ✅ User menu with logout functionality
   - ✅ Chat sidebar with conversation history
   - ✅ Collapsible sidebar functionality
   - ✅ Mobile responsive design

3. Key differences from AppLayout:
   - Sidebar is now dedicated to chat history only
   - Navigation moved to header
   - User controls in header dropdown
   - Automatic integration with Supabase chat history

4. Environment variables needed:
   - NEXT_PUBLIC_SUPABASE_URL
   - NEXT_PUBLIC_SUPABASE_ANON_KEY
   
5. Database requirements:
   - user_conversations table (already created)
   - conversation_messages table (already created)
   - Proper RLS policies (already implemented)

=== MIGRATION CHECKLIST ===

□ Replace AppLayout imports with ChatLayout
□ Update page component structure
□ Test authentication flow
□ Test conversation creation/selection
□ Test responsive design
□ Test logout functionality
□ Verify environment variables
□ Test database connectivity

*/
