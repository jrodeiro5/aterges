// types/index.ts
// Central exports for all types

export * from './chat';

// Re-export commonly used types for convenience
export type {
  User,
  Conversation,
  Message,
  ChatState,
  ConversationCategory,
  MessageRole,
  NavigationItem
} from './chat';
