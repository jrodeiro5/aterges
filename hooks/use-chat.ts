// hooks/use-chat.ts
'use client';

import { useState, useEffect, useCallback } from 'react';
import { createClient } from '@supabase/supabase-js';
import { 
  Conversation, 
  Message, 
  ChatState, 
  UserConversation, 
  ConversationMessage,
  dbConversationToConversation,
  dbMessageToMessage,
  ConversationCategory 
} from '@/types/chat';

// Initialize Supabase client (using existing supabase client if available)
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

const supabase = createClient(supabaseUrl, supabaseKey);

export function useChat(userId: string) {
  const [state, setState] = useState<ChatState>({
    conversations: [],
    currentConversationId: null,
    messages: [],
    loading: true,
    error: null,
    sidebarCollapsed: false
  });

  // Load conversations from Supabase
  const loadConversations = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, loading: true }));
      
      const { data, error } = await supabase
        .from('user_conversations')
        .select('*')
        .eq('user_id', userId)
        .eq('is_deleted', false)
        .order('updated_at', { ascending: false });

      if (error) throw error;

      const conversations = (data || []).map(dbConversationToConversation);

      setState(prev => ({
        ...prev,
        conversations,
        loading: false,
        error: null
      }));
    } catch (error) {
      console.error('Error loading conversations:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Error loading conversations',
        loading: false
      }));
    }
  }, [userId]);

  // Load messages for a specific conversation
  const loadMessages = useCallback(async (conversationId: string) => {
    try {
      const { data, error } = await supabase
        .from('conversation_messages')
        .select('*')
        .eq('conversation_id', conversationId)
        .order('created_at', { ascending: true });

      if (error) throw error;

      const messages = (data || []).map(dbMessageToMessage);

      setState(prev => ({
        ...prev,
        messages,
        currentConversationId: conversationId
      }));
    } catch (error) {
      console.error('Error loading messages:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Error loading messages'
      }));
    }
  }, []);

  // Create new conversation
  const createConversation = useCallback(async (title: string = 'Nueva conversación', category: ConversationCategory = 'general') => {
    try {
      const { data, error } = await supabase
        .from('user_conversations')
        .insert({
          user_id: userId,
          title,
          category
        })
        .select()
        .single();

      if (error) throw error;

      const newConversation = dbConversationToConversation(data as UserConversation);

      setState(prev => ({
        ...prev,
        conversations: [newConversation, ...prev.conversations],
        currentConversationId: newConversation.id,
        messages: []
      }));

      return newConversation.id;
    } catch (error) {
      console.error('Error creating conversation:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Error creating conversation'
      }));
      return null;
    }
  }, [userId]);

  // Add message to conversation
  const addMessage = useCallback(async (conversationId: string, role: 'user' | 'assistant', content: string, metadata?: Record<string, any>) => {
    try {
      const { data, error } = await supabase
        .from('conversation_messages')
        .insert({
          conversation_id: conversationId,
          role,
          content,
          metadata: metadata || {}
        })
        .select()
        .single();

      if (error) throw error;

      const newMessage = dbMessageToMessage(data as ConversationMessage);

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, newMessage]
      }));

      // Update conversation's updated_at and last_message_at (triggers handle message_count)
      await supabase
        .from('user_conversations')
        .update({ 
          updated_at: new Date().toISOString(),
          last_message_at: new Date().toISOString()
        })
        .eq('id', conversationId);

      return newMessage;
    } catch (error) {
      console.error('Error adding message:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Error adding message'
      }));
      return null;
    }
  }, []);

  // Pin/unpin conversation
  const togglePinConversation = useCallback(async (conversationId: string) => {
    try {
      const conversation = state.conversations.find(c => c.id === conversationId);
      if (!conversation) return;

      const { error } = await supabase
        .from('user_conversations')
        .update({ is_pinned: !conversation.isPinned })
        .eq('id', conversationId);

      if (error) throw error;

      setState(prev => ({
        ...prev,
        conversations: prev.conversations.map(conv =>
          conv.id === conversationId 
            ? { ...conv, isPinned: !conv.isPinned }
            : conv
        )
      }));
    } catch (error) {
      console.error('Error updating conversation:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Error updating conversation'
      }));
    }
  }, [state.conversations]);

  // Delete conversation (soft delete)
  const deleteConversation = useCallback(async (conversationId: string) => {
    try {
      const { error } = await supabase
        .from('user_conversations')
        .update({ is_deleted: true })
        .eq('id', conversationId);

      if (error) throw error;

      setState(prev => ({
        ...prev,
        conversations: prev.conversations.filter(conv => conv.id !== conversationId),
        currentConversationId: prev.currentConversationId === conversationId 
          ? prev.conversations[0]?.id || null 
          : prev.currentConversationId,
        messages: prev.currentConversationId === conversationId ? [] : prev.messages
      }));
    } catch (error) {
      console.error('Error deleting conversation:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Error deleting conversation'
      }));
    }
  }, []);

  // Archive conversation
  const archiveConversation = useCallback(async (conversationId: string) => {
    try {
      const conversation = state.conversations.find(c => c.id === conversationId);
      if (!conversation) return;

      const { error } = await supabase
        .from('user_conversations')
        .update({ is_archived: !conversation.isArchived })
        .eq('id', conversationId);

      if (error) throw error;

      setState(prev => ({
        ...prev,
        conversations: prev.conversations.map(conv =>
          conv.id === conversationId 
            ? { ...conv, isArchived: !conv.isArchived }
            : conv
        )
      }));
    } catch (error) {
      console.error('Error archiving conversation:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Error archiving conversation'
      }));
    }
  }, [state.conversations]);

  // Update conversation title
  const updateConversationTitle = useCallback(async (conversationId: string, title: string) => {
    try {
      const { error } = await supabase
        .from('user_conversations')
        .update({ title })
        .eq('id', conversationId);

      if (error) throw error;

      setState(prev => ({
        ...prev,
        conversations: prev.conversations.map(conv =>
          conv.id === conversationId 
            ? { ...conv, title }
            : conv
        )
      }));
    } catch (error) {
      console.error('Error updating title:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Error updating title'
      }));
    }
  }, []);

  // Select conversation
  const selectConversation = useCallback((conversationId: string) => {
    loadMessages(conversationId);
  }, [loadMessages]);

  // Toggle sidebar collapse
  const toggleSidebar = useCallback(() => {
    setState(prev => {
      const newCollapsed = !prev.sidebarCollapsed;
      localStorage.setItem('chat-sidebar-collapsed', JSON.stringify(newCollapsed));
      return {
        ...prev,
        sidebarCollapsed: newCollapsed
      };
    });
  }, []);

  // Load sidebar state from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('chat-sidebar-collapsed');
    if (saved !== null) {
      setState(prev => ({
        ...prev,
        sidebarCollapsed: JSON.parse(saved)
      }));
    }
  }, []);

  // Initial load
  useEffect(() => {
    if (userId) {
      loadConversations();
    }
  }, [userId, loadConversations]);

  // Set up real-time subscriptions
  useEffect(() => {
    if (!userId) return;

    // Subscribe to conversation changes
    const conversationsSubscription = supabase
      .channel('user_conversations')
      .on('postgres_changes', 
        { 
          event: '*', 
          schema: 'public', 
          table: 'user_conversations',
          filter: `user_id=eq.${userId}`
        }, 
        () => {
          loadConversations();
        }
      )
      .subscribe();

    // Subscribe to message changes for current conversation
    let messagesSubscription: any = null;
    if (state.currentConversationId) {
      messagesSubscription = supabase
        .channel('conversation_messages')
        .on('postgres_changes',
          {
            event: '*',
            schema: 'public',
            table: 'conversation_messages',
            filter: `conversation_id=eq.${state.currentConversationId}`
          },
          () => {
            if (state.currentConversationId) {
              loadMessages(state.currentConversationId);
            }
          }
        )
        .subscribe();
    }

    return () => {
      conversationsSubscription.unsubscribe();
      if (messagesSubscription) {
        messagesSubscription.unsubscribe();
      }
    };
  }, [userId, state.currentConversationId, loadConversations, loadMessages]);

  return {
    // State
    conversations: state.conversations,
    currentConversationId: state.currentConversationId,
    messages: state.messages,
    loading: state.loading,
    error: state.error,
    sidebarCollapsed: state.sidebarCollapsed,

    // Actions
    createConversation,
    selectConversation,
    addMessage,
    togglePinConversation,
    deleteConversation,
    archiveConversation,
    updateConversationTitle,
    loadConversations,
    toggleSidebar
  };
}
