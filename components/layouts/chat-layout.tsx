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
      // Use replace instead of push to avoid history issues
      router.replace('/login');
    }
  }, [user, authLoading, router]);

  // Handle logout
  const handleLogout = async () => {
    try {
      await signOut();
      router.replace('/login');
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  // Handle new conversation
  const handleNewConversation = async () => {
    const conversationId = await createConversation();
    if (conversationId) {
      selectConversation(conversationId);
      // Auto-close sidebar on mobile after selecting conversation
      if (window.innerWidth < 1024 && !sidebarCollapsed) {
        toggleSidebar();
      }
    }
  };

  // Handle conversation selection with mobile auto-close
  const handleSelectConversation = (conversationId: string) => {
    selectConversation(conversationId);
    // Auto-close sidebar on mobile after selecting conversation
    if (window.innerWidth < 1024 && !sidebarCollapsed) {
      toggleSidebar();
    }
  };

  // Show loading state while auth is loading
  if (authLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="text-lg font-medium text-muted-foreground">Cargando...</div>
        </div>
      </div>
    );
  }

  // Show loading state while redirecting to login
  if (!user) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="text-lg font-medium text-muted-foreground">Redirigiendo...</div>
        </div>
      </div>
    );
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
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
          onPinConversation={togglePinConversation}
          onDeleteConversation={deleteConversation}
          onArchiveConversation={archiveConversation}
          isCollapsed={sidebarCollapsed}
          onClose={toggleSidebar} // Close sidebar on mobile when clicking backdrop
        />

        {/* Main Chat Area */}
        <main className={cn(
          "flex-1 flex flex-col overflow-hidden",
          "lg:relative", // Desktop: always relative
          !sidebarCollapsed && "lg:ml-0" // Mobile: no margin, Desktop: no margin when sidebar visible
        )}>
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
