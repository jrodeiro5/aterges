// types/chat.ts
// TypeScript types that match the Supabase database schema

export interface User {
  id: string;
  email: string;
  name?: string;
  avatar?: string;
}

export interface UserConversation {
  id: string;
  user_id: string;
  title: string;
  category: ConversationCategory;
  is_pinned: boolean;
  is_archived: boolean;
  is_deleted: boolean;
  message_count: number;
  created_at: string;
  updated_at: string;
  last_message_at: string;
}

export interface ConversationMessage {
  id: string;
  conversation_id: string;
  role: MessageRole;
  content: string;
  metadata: Record<string, any>;
  created_at: string;
}

export type ConversationCategory = 
  | 'general'
  | 'analytics' 
  | 'marketing'
  | 'automation'
  | 'reports'
  | 'archived';

export type MessageRole = 'user' | 'assistant' | 'system';

// Frontend display types (mapped from database types)
export interface Conversation {
  id: string;
  title: string;
  category: ConversationCategory;
  isPinned: boolean;
  isArchived: boolean;
  isDeleted: boolean;
  messageCount: number;
  createdAt: string;
  updatedAt: string;
  lastMessageAt: string;
}

export interface Message {
  id: string;
  conversationId: string;
  role: MessageRole;
  content: string;
  metadata?: Record<string, any>;
  createdAt: string;
}

// Chat state management
export interface ChatState {
  conversations: Conversation[];
  currentConversationId: string | null;
  messages: Message[];
  loading: boolean;
  error: string | null;
  sidebarCollapsed: boolean;
}

// Component props
export interface ChatSidebarProps {
  conversations: Conversation[];
  currentConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  onPinConversation: (id: string) => void;
  onDeleteConversation: (id: string) => void;
  onArchiveConversation: (id: string) => void;
  isCollapsed: boolean;
}

export interface MainHeaderProps {
  user: User;
  onSidebarToggle: () => void;
  onLogout: () => void;
}

export interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  onSelect: () => void;
  onPin: () => void;
  onDelete: () => void;
  onArchive: () => void;
}

// Navigation types
export interface NavigationItem {
  href: string;
  label: string;
  description: string;
  icon?: React.ComponentType<{ className?: string }>;
}

// Utility functions for type conversion
export function dbConversationToConversation(dbConv: UserConversation): Conversation {
  return {
    id: dbConv.id,
    title: dbConv.title,
    category: dbConv.category,
    isPinned: dbConv.is_pinned,
    isArchived: dbConv.is_archived,
    isDeleted: dbConv.is_deleted,
    messageCount: dbConv.message_count,
    createdAt: dbConv.created_at,
    updatedAt: dbConv.updated_at,
    lastMessageAt: dbConv.last_message_at
  };
}

export function dbMessageToMessage(dbMessage: ConversationMessage): Message {
  return {
    id: dbMessage.id,
    conversationId: dbMessage.conversation_id,
    role: dbMessage.role,
    content: dbMessage.content,
    metadata: dbMessage.metadata,
    createdAt: dbMessage.created_at
  };
}

// Category configuration
export const CONVERSATION_CATEGORIES: Record<ConversationCategory, {
  label: string;
  icon: string;
  color: string;
}> = {
  general: {
    label: 'General',
    icon: '💬',
    color: 'text-gray-600'
  },
  analytics: {
    label: 'Analytics',
    icon: '📊',
    color: 'text-blue-600'
  },
  marketing: {
    label: 'Marketing',
    icon: '📈',
    color: 'text-green-600'
  },
  automation: {
    label: 'Automatización',
    icon: '⚙️',
    color: 'text-purple-600'
  },
  reports: {
    label: 'Informes',
    icon: '📋',
    color: 'text-orange-600'
  },
  archived: {
    label: 'Archivadas',
    icon: '📦',
    color: 'text-gray-400'
  }
};

// Date grouping utilities
export type DateGroup = 'Hoy' | 'Ayer' | 'Semana pasada' | 'Mes pasado' | 'Más antiguas';

export function getDateGroup(dateString: string): DateGroup {
  const date = new Date(dateString);
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

  if (diffInDays === 0) return 'Hoy';
  if (diffInDays === 1) return 'Ayer';
  if (diffInDays <= 7) return 'Semana pasada';
  if (diffInDays <= 30) return 'Mes pasado';
  return 'Más antiguas';
}

// API response types
export interface CreateConversationRequest {
  title?: string;
  category?: ConversationCategory;
}

export interface CreateConversationResponse {
  conversation: Conversation;
}

export interface AddMessageRequest {
  conversationId: string;
  role: MessageRole;
  content: string;
  metadata?: Record<string, any>;
}

export interface AddMessageResponse {
  message: Message;
}

// Error types
export interface ChatError {
  code: string;
  message: string;
  details?: any;
}
