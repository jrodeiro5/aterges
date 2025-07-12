// components/chat/chat-sidebar.tsx
'use client';

import React, { useState } from 'react';
import { Plus, Pin, MoreHorizontal, MessageSquare, Calendar, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { 
  Conversation, 
  ChatSidebarProps, 
  CONVERSATION_CATEGORIES,
  getDateGroup,
  truncateTitle
} from '@/types/chat';
import { cn } from '@/lib/utils';

function ConversationItem({ 
  conversation, 
  isActive, 
  onSelect, 
  onPin, 
  onDelete,
  onArchive 
}: {
  conversation: Conversation;
  isActive: boolean;
  onSelect: () => void;
  onPin: () => void;
  onDelete: () => void;
  onArchive: () => void;
}) {
  const categoryConfig = CONVERSATION_CATEGORIES[conversation.category];
  const CategoryIcon = categoryConfig.icon;
  const truncatedTitle = truncateTitle(conversation.title);

  return (
    <div className={cn(
      "group relative flex items-center gap-3 px-4 py-3 rounded-lg cursor-pointer",
      "hover:bg-muted/50 transition-colors duration-150",
      isActive ? "bg-muted" : ""
    )}>
      <div className="flex-1 min-w-0" onClick={onSelect}>
        <div className="flex items-center gap-2">
          <CategoryIcon 
            className={cn("h-4 w-4 flex-shrink-0", categoryConfig.color)} 
          />
          <p className="text-sm font-medium leading-tight" title={conversation.title}>
            {truncatedTitle}
          </p>
          {conversation.isPinned && (
            <Pin className="h-3 w-3 text-muted-foreground flex-shrink-0" />
          )}
        </div>
        <div className="flex items-center gap-1 mt-1">
          <span className="text-xs text-muted-foreground">
            {conversation.messageCount} mensajes
          </span>
        </div>
      </div>
      
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button 
            variant="ghost" 
            size="sm" 
            className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <MoreHorizontal className="h-3 w-3" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48">
          <DropdownMenuItem onClick={onPin}>
            <Pin className="h-4 w-4 mr-2" />
            {conversation.isPinned ? 'Desfijar' : 'Fijar conversación'}
          </DropdownMenuItem>
          <DropdownMenuItem onClick={onArchive}>
            <Calendar className="h-4 w-4 mr-2" />
            {conversation.isArchived ? 'Desarchivar' : 'Archivar'}
          </DropdownMenuItem>
          <DropdownMenuItem onClick={onDelete} className="text-destructive">
            <MessageSquare className="h-4 w-4 mr-2" />
            Eliminar
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}

export function ChatSidebar({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  onPinConversation,
  onDeleteConversation,
  onArchiveConversation,
  isCollapsed
}: ChatSidebarProps) {
  const [showAllConversations, setShowAllConversations] = useState(false);

  // Filter out archived and deleted conversations for main view
  const activeConversations = conversations.filter(c => !c.isArchived && !c.isDeleted);
  
  // Group conversations
  const pinnedConversations = activeConversations.filter(c => c.isPinned);
  const unpinnedConversations = activeConversations.filter(c => !c.isPinned);
  
  // Group unpinned by date
  const groupedConversations = unpinnedConversations.reduce((groups, conv) => {
    const dateGroup = getDateGroup(conv.createdAt);
    if (!groups[dateGroup]) groups[dateGroup] = [];
    groups[dateGroup].push(conv);
    return groups;
  }, {} as Record<string, Conversation[]>);

  const visibleGroups = showAllConversations 
    ? Object.entries(groupedConversations)
    : Object.entries(groupedConversations).slice(0, 2);

  if (isCollapsed) {
    return (
      <div className="w-16 h-full border-r bg-background flex flex-col items-center py-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={onNewConversation}
          className="w-10 h-10 mb-4"
          title="Nueva Conversación"
        >
          <Plus className="h-4 w-4" />
        </Button>
        <div className="space-y-2">
          {activeConversations.slice(0, 6).map(conv => {
            const categoryConfig = CONVERSATION_CATEGORIES[conv.category];
            const CategoryIcon = categoryConfig.icon;
            return (
              <Button
                key={conv.id}
                variant="ghost"
                size="sm"
                onClick={() => onSelectConversation(conv.id)}
                className={cn(
                  "w-10 h-10 relative",
                  conv.id === currentConversationId ? "bg-muted" : ""
                )}
                title={conv.title}
              >
                <CategoryIcon className="h-4 w-4" />
                {conv.isPinned && (
                  <div className="absolute -top-1 -right-1 w-2 h-2 bg-primary rounded-full" />
                )}
              </Button>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className="w-80 h-full border-r bg-background flex flex-col">
      {/* Header */}
      <div className="p-6 border-b">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Conversaciones
          </h2>
        </div>
        
        {/* New Conversation Button */}
        <Button 
          onClick={onNewConversation}
          className="w-full justify-start gap-2 font-medium"
          variant="outline"
        >
          <Plus className="h-4 w-4" />
          Nueva Conversación
        </Button>
      </div>

      {/* Conversations List */}
      <ScrollArea className="flex-1 px-2">
        <div className="space-y-1 py-3">
          {/* Pinned Conversations */}
          {pinnedConversations.length > 0 && (
            <div className="mb-6">
              <div className="flex items-center gap-2 px-4 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                <Pin className="h-3 w-3" />
                Fijadas
              </div>
              {pinnedConversations.map(conversation => (
                <ConversationItem
                  key={conversation.id}
                  conversation={conversation}
                  isActive={conversation.id === currentConversationId}
                  onSelect={() => onSelectConversation(conversation.id)}
                  onPin={() => onPinConversation(conversation.id)}
                  onDelete={() => onDeleteConversation(conversation.id)}
                  onArchive={() => onArchiveConversation(conversation.id)}
                />
              ))}
            </div>
          )}

          {/* Grouped Conversations by Date */}
          {visibleGroups.map(([dateGroup, convs]) => (
            <div key={dateGroup} className="mb-6">
              <div className="flex items-center gap-2 px-4 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                <Calendar className="h-3 w-3" />
                {dateGroup}
              </div>
              {convs.map(conversation => (
                <ConversationItem
                  key={conversation.id}
                  conversation={conversation}
                  isActive={conversation.id === currentConversationId}
                  onSelect={() => onSelectConversation(conversation.id)}
                  onPin={() => onPinConversation(conversation.id)}
                  onDelete={() => onDeleteConversation(conversation.id)}
                  onArchive={() => onArchiveConversation(conversation.id)}
                />
              ))}
            </div>
          ))}

          {/* Show More Button */}
          {!showAllConversations && Object.keys(groupedConversations).length > 2 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAllConversations(true)}
              className="w-full justify-start text-muted-foreground font-medium mx-2"
            >
              <ChevronDown className="h-4 w-4 mr-2" />
              Ver más conversaciones
            </Button>
          )}

          {activeConversations.length === 0 && (
            <div className="text-center py-12 px-4 text-muted-foreground">
              <MessageSquare className="h-8 w-8 mx-auto mb-3 opacity-50" />
              <p className="text-sm font-medium mb-1">No hay conversaciones</p>
              <p className="text-xs">Crea una nueva para empezar</p>
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
