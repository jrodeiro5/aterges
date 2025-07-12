-- =====================================================
-- Aterges Chat Interface Database Schema
-- Migration 001: Chat Conversations Support
-- =====================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- Table: user_conversations
-- Purpose: Store chat conversation metadata
-- =====================================================

CREATE TABLE IF NOT EXISTS user_conversations (
    -- Primary identifier
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- User relationship (references Supabase auth.users)
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Conversation metadata
    title VARCHAR(255) NOT NULL DEFAULT 'Nueva conversación',
    category VARCHAR(50) DEFAULT 'general' CHECK (category IN ('general', 'analytics', 'marketing', 'automation', 'reports', 'archived')),
    
    -- Status flags
    is_pinned BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    -- Metrics
    message_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- Table: conversation_messages  
-- Purpose: Store individual chat messages
-- =====================================================

CREATE TABLE IF NOT EXISTS conversation_messages (
    -- Primary identifier
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Conversation relationship
    conversation_id UUID NOT NULL REFERENCES user_conversations(id) ON DELETE CASCADE,
    
    -- Message content
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    
    -- Optional metadata (JSON for flexibility)
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- Indexes for Performance
-- =====================================================

-- User conversations queries (most common)
CREATE INDEX IF NOT EXISTS idx_user_conversations_user_id 
    ON user_conversations(user_id, updated_at DESC);

-- Active conversations (not deleted/archived)
CREATE INDEX IF NOT EXISTS idx_user_conversations_active 
    ON user_conversations(user_id, is_deleted, is_archived, updated_at DESC) 
    WHERE is_deleted = FALSE;

-- Pinned conversations
CREATE INDEX IF NOT EXISTS idx_user_conversations_pinned 
    ON user_conversations(user_id, is_pinned, updated_at DESC) 
    WHERE is_pinned = TRUE;

-- Category filtering
CREATE INDEX IF NOT EXISTS idx_user_conversations_category 
    ON user_conversations(user_id, category, updated_at DESC);

-- Message retrieval by conversation
CREATE INDEX IF NOT EXISTS idx_conversation_messages_conversation_id 
    ON conversation_messages(conversation_id, created_at ASC);

-- Message search (if needed for full-text search later)
CREATE INDEX IF NOT EXISTS idx_conversation_messages_content 
    ON conversation_messages USING GIN(to_tsvector('spanish', content));

-- =====================================================
-- Row Level Security (RLS) Policies
-- =====================================================

-- Enable RLS on both tables
ALTER TABLE user_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own conversations
CREATE POLICY IF NOT EXISTS "Users can view own conversations" 
    ON user_conversations FOR SELECT 
    USING (auth.uid() = user_id);

-- Policy: Users can create their own conversations
CREATE POLICY IF NOT EXISTS "Users can create own conversations" 
    ON user_conversations FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own conversations
CREATE POLICY IF NOT EXISTS "Users can update own conversations" 
    ON user_conversations FOR UPDATE 
    USING (auth.uid() = user_id);

-- Policy: Users can delete their own conversations
CREATE POLICY IF NOT EXISTS "Users can delete own conversations" 
    ON user_conversations FOR DELETE 
    USING (auth.uid() = user_id);

-- Policy: Users can view messages from their conversations
CREATE POLICY IF NOT EXISTS "Users can view own messages" 
    ON conversation_messages FOR SELECT 
    USING (
        conversation_id IN (
            SELECT id FROM user_conversations WHERE user_id = auth.uid()
        )
    );

-- Policy: Users can create messages in their conversations
CREATE POLICY IF NOT EXISTS "Users can create own messages" 
    ON conversation_messages FOR INSERT 
    WITH CHECK (
        conversation_id IN (
            SELECT id FROM user_conversations WHERE user_id = auth.uid()
        )
    );

-- Policy: Users can update messages in their conversations
CREATE POLICY IF NOT EXISTS "Users can update own messages" 
    ON conversation_messages FOR UPDATE 
    USING (
        conversation_id IN (
            SELECT id FROM user_conversations WHERE user_id = auth.uid()
        )
    );

-- Policy: Users can delete messages in their conversations
CREATE POLICY IF NOT EXISTS "Users can delete own messages" 
    ON conversation_messages FOR DELETE 
    USING (
        conversation_id IN (
            SELECT id FROM user_conversations WHERE user_id = auth.uid()
        )
    );

-- =====================================================
-- Triggers for Automatic Updates
-- =====================================================

-- Function: Update conversation updated_at timestamp
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the parent conversation's updated_at and last_message_at
    UPDATE user_conversations 
    SET 
        updated_at = NOW(),
        last_message_at = NOW(),
        message_count = (
            SELECT COUNT(*) 
            FROM conversation_messages 
            WHERE conversation_id = NEW.conversation_id
        )
    WHERE id = NEW.conversation_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Update conversation when message is added
DROP TRIGGER IF EXISTS trigger_update_conversation_on_message ON conversation_messages;
CREATE TRIGGER trigger_update_conversation_on_message
    AFTER INSERT OR DELETE ON conversation_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_timestamp();

-- Function: Generate conversation title from first message
CREATE OR REPLACE FUNCTION generate_conversation_title()
RETURNS TRIGGER AS $$
BEGIN
    -- If this is the first user message and title is still default
    IF NEW.role = 'user' AND (
        SELECT title FROM user_conversations WHERE id = NEW.conversation_id
    ) = 'Nueva conversación' THEN
        
        -- Generate title from first 50 characters of the message
        UPDATE user_conversations 
        SET title = CASE 
            WHEN LENGTH(NEW.content) > 50 
            THEN LEFT(NEW.content, 50) || '...'
            ELSE NEW.content
        END
        WHERE id = NEW.conversation_id;
        
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-generate conversation titles
DROP TRIGGER IF EXISTS trigger_generate_conversation_title ON conversation_messages;
CREATE TRIGGER trigger_generate_conversation_title
    AFTER INSERT ON conversation_messages
    FOR EACH ROW
    EXECUTE FUNCTION generate_conversation_title();

-- =====================================================
-- Useful Views for Common Queries
-- =====================================================

-- View: Recent conversations with last message preview
CREATE OR REPLACE VIEW recent_conversations AS
SELECT 
    c.id,
    c.user_id,
    c.title,
    c.category,
    c.is_pinned,
    c.is_archived,
    c.message_count,
    c.created_at,
    c.updated_at,
    c.last_message_at,
    -- Last message preview
    (
        SELECT content 
        FROM conversation_messages m 
        WHERE m.conversation_id = c.id 
        ORDER BY m.created_at DESC 
        LIMIT 1
    ) as last_message_preview,
    -- Last message role
    (
        SELECT role 
        FROM conversation_messages m 
        WHERE m.conversation_id = c.id 
        ORDER BY m.created_at DESC 
        LIMIT 1
    ) as last_message_role
FROM user_conversations c
WHERE c.is_deleted = FALSE
ORDER BY 
    c.is_pinned DESC,
    c.updated_at DESC;

-- =====================================================
-- Sample Data (Optional - for testing)
-- =====================================================

-- Insert sample conversation (only if testing)
-- Note: This will only work if you have a user in auth.users
/*
INSERT INTO user_conversations (user_id, title, category, is_pinned) 
VALUES (
    'YOUR_USER_ID_HERE', 
    'Análisis de tráfico web', 
    'analytics', 
    true
);
*/

-- =====================================================
-- Migration Complete
-- =====================================================

-- Log the migration
DO $$
BEGIN
    RAISE NOTICE 'Migration 001: Chat Conversations Support - COMPLETED';
    RAISE NOTICE 'Tables created: user_conversations, conversation_messages';
    RAISE NOTICE 'Indexes created: 6 performance indexes';
    RAISE NOTICE 'RLS policies: Enabled with user-based access control';
    RAISE NOTICE 'Triggers: Auto-update timestamps and titles';
    RAISE NOTICE 'Views: recent_conversations for easy querying';
END $$;
