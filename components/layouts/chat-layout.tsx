// components/layouts/chat-layout.tsx
'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { MainHeader } from './main-header';
import { ChatSidebar } from '../chat/chat-sidebar';
import { useSupabaseAuth } from '@/lib/auth-supabase-fixed';
import { useChat } from '@/hooks/use-chat';
import { User } from '@/types/chat';
import { cn } from '@/lib/utils';

interface ChatLayoutProps {
  children: React.ReactNode;
}

export function ChatLayout({ children }: ChatLayoutProps) {
  const router = useRouter();
  
  // Use existing Supabase auth
  const { user: authUser, loading: authLoading, signOut } = useSupabaseAuth();
  
  // Convert authUser to our User type
  const user: User | null = authUser ? {
    id: authUser.id,
    email: authUser.email || '',
    name: (authUser as any).user_metadata?.name || (authUser as any).user_metadata?.full_name || authUser.email?.split('@')[0] || 'Usuario'
  } : null;

  // Use chat hook with user ID
  const {
    conversations,
    currentConversationId,
    sidebarCollapsed,
    loading: chatLoading,
    error: chatError,
    createConversation,
    selectConversation,
    togglePinConversation,
    deleteConversation,
    archiveConversation,
    toggleSidebar
  } = useChat(user?.id || '');

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  // Handle logout
  const handleLogout = async () => {
    try {
      await signOut();
      router.push('/login');
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  // Handle new conversation
  const handleNewConversation = async () => {
    const conversationId = await createConversation();
    if (conversationId) {
      selectConversation(conversationId);
    }
  };

  // Show loading state
  if (authLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="text-lg font-medium text-muted-foreground">Cargando...</div>
        </div>
      </div>
    );
  }

  // Don't render if not authenticated
  if (!user) {
    return null;
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* Header */}
      <MainHeader
        user={user}
        onSidebarToggle={toggleSidebar}
        onLogout={handleLogout}
      />

      {/* Main Content Area */}
      <div className="flex flex-1 pt-14 overflow-hidden">
        {/* Chat Sidebar */}
        <ChatSidebar
          conversations={conversations}
          currentConversationId={currentConversationId}
          onSelectConversation={selectConversation}
          onNewConversation={handleNewConversation}
          onPinConversation={togglePinConversation}
          onDeleteConversation={deleteConversation}
          onArchiveConversation={archiveConversation}
          isCollapsed={sidebarCollapsed}
        />

        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {/* Error Display */}
          {chatError && (
            <div className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-2 text-sm">
              Error: {chatError}
            </div>
          )}
          
          {/* Page Content */}
          {children}
        </main>
      </div>
    </div>
  );
}

// Example wrapper for pages that need chat layout
export function withChatLayout<P extends object>(
  Component: React.ComponentType<P>
) {
  return function ChatLayoutWrapper(props: P) {
    return (
      <ChatLayout>
        <Component {...props} />
      </ChatLayout>
    );
  };
}
