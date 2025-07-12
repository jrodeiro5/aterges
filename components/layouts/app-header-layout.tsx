// components/layouts/app-header-layout.tsx
'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { MainHeader } from './main-header';
import { useSupabaseAuth } from '@/lib/auth-supabase-fixed';
import { User } from '@/types/chat';

interface AppHeaderLayoutProps {
  children: React.ReactNode;
}

export function AppHeaderLayout({ children }: AppHeaderLayoutProps) {
  const router = useRouter();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  // Use existing Supabase auth
  const { user: authUser, loading: authLoading, signOut } = useSupabaseAuth();
  
  // Convert authUser to our User type
  const user: User | null = authUser ? {
    id: authUser.id,
    email: authUser.email || '',
    name: (authUser as any).user_metadata?.name || (authUser as any).user_metadata?.full_name || authUser.email?.split('@')[0] || 'Usuario'
  } : null;

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  const handleLogout = async () => {
    try {
      await signOut();
      router.push('/login');
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  // Show loading state
  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-muted-foreground font-medium">Cargando...</div>
        </div>
      </div>
    );
  }

  // Don't render if no user
  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <MainHeader 
        user={user}
        onSidebarToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        onLogout={handleLogout}
      />
      
      {/* Main Content - No Sidebar */}
      <main className="pt-14">
        {children}
      </main>
    </div>
  );
}
