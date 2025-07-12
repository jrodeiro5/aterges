"use client"

import { ReactNode, useEffect, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { ThemeToggle } from '@/components/theme-toggle';
import { 
  LayoutDashboard, 
  Bot, 
  Settings, 
  LogOut,
  Menu,
  X,
  MessageSquare,
  Database
} from 'lucide-react';
import { useSupabaseAuth, AuthUser } from '@/lib/auth-supabase-fixed';
import { cn } from '@/lib/utils';

interface AppLayoutProps {
  children: ReactNode;
}

const navigation = [
  {
    name: 'Dashboard',
    href: '/app/dashboard',
    icon: LayoutDashboard,
    description: 'Chat con IA y resumen de actividad'
  },
  {
    name: 'Agentes',
    href: '/app/agents',
    icon: Bot,
    description: 'Gestiona tus agentes de IA'
  },
  {
    name: 'Integraciones',
    href: '/app/integrations',
    icon: Database,
    description: 'Conecta tus APIs y servicios'
  },
  {
    name: 'Configuración',
    href: '/app/settings',
    icon: Settings,
    description: 'Perfil, seguridad y facturación'
  },
];

export function AppLayout({ children }: AppLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  
  // Use Supabase auth instead of old auth service
  const { user, loading, signOut } = useSupabaseAuth();

  // Load collapse state from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('sidebar-collapsed');
    if (saved !== null) {
      setSidebarCollapsed(JSON.parse(saved));
    }
  }, []);

  // Save collapse state when it changes
  useEffect(() => {
    localStorage.setItem('sidebar-collapsed', JSON.stringify(sidebarCollapsed));
  }, [sidebarCollapsed]);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-pulse flex items-center space-x-2">
          <Image
            src="/aterges_logo-removebg-preview.png"
            alt="Aterges AI"
            width={320}
            height={85}
            className="h-20 w-auto opacity-60 object-contain"
            style={{ objectPosition: 'left center' }}
          />
          <span className="text-lg font-medium">Cargando...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const currentPage = navigation.find(item => item.href === pathname);

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={cn(
        "fixed inset-y-0 left-0 z-50 bg-card border-r border-border transform transition-all duration-300 ease-in-out lg:translate-x-0",
        // Mobile behavior
        sidebarOpen ? "translate-x-0" : "-translate-x-full",
        // Desktop behavior
        "lg:translate-x-0",
        // Desktop width based on collapse state
        sidebarCollapsed ? "lg:w-20" : "lg:w-80",
        // Mobile always full width
        "w-80"
      )}>
        <div className="flex h-full flex-col">
          {/* Sidebar header */}
          <div className="flex h-28 items-center justify-between px-6 border-b border-border">
            <Link href="/app/dashboard" className="flex items-center">
              <Image
                src="/aterges_logo-removebg-preview.png"
                alt="Aterges AI"
                width={320}
                height={85}
                className={cn(
                  "h-20 w-auto object-contain transition-all duration-300",
                  sidebarCollapsed ? "scale-75 opacity-60" : ""
                )}
                priority
                style={{ objectPosition: 'left center' }}
              />
            </Link>
            <div className="flex items-center space-x-2">
              {/* Desktop collapse button */}
              <Button
                variant="ghost"
                size="sm"
                className="hidden lg:flex"
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                title={sidebarCollapsed ? "Expandir sidebar" : "Colapsar sidebar"}
              >
                {sidebarCollapsed ? (
                  <Menu className="h-4 w-4" />
                ) : (
                  <X className="h-4 w-4" />
                )}
              </Button>
              {/* Mobile close button */}
              <Button
                variant="ghost"
                size="sm"
                className="lg:hidden"
                onClick={() => setSidebarOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-2 p-4">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "group flex rounded-lg px-3 py-3 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground",
                    isActive 
                      ? "bg-accent text-accent-foreground shadow-sm" 
                      : "text-muted-foreground hover:text-foreground",
                    // Adjust layout based on collapse state
                    sidebarCollapsed ? "flex-col items-center space-y-1 lg:px-2" : "flex-col space-y-1"
                  )}
                  onClick={() => setSidebarOpen(false)}
                  title={sidebarCollapsed ? item.name : ""}
                >
                  <div className={cn(
                    "flex items-center",
                    sidebarCollapsed ? "lg:justify-center" : "space-x-3"
                  )}>
                    <Icon className="h-4 w-4 shrink-0" />
                    <span className={cn(
                      "font-medium transition-all duration-300",
                      sidebarCollapsed ? "lg:hidden" : ""
                    )}>
                      {item.name}
                    </span>
                  </div>
                  <p className={cn(
                    "text-xs text-muted-foreground group-hover:text-muted-foreground/80 transition-all duration-300",
                    sidebarCollapsed ? "lg:hidden" : "pl-7"
                  )}>
                    {item.description}
                  </p>
                </Link>
              );
            })}
          </nav>

          {/* Quick Actions */}
          <div className="border-t border-border p-4 space-y-2">
            <p className={cn(
              "text-xs font-medium text-muted-foreground uppercase tracking-wider px-3 transition-all duration-300",
              sidebarCollapsed ? "lg:hidden" : ""
            )}>
              Acciones Rápidas
            </p>
            <Button
              variant="ghost"
              size="sm"
              className={cn(
                "w-full text-muted-foreground hover:text-foreground transition-all duration-300",
                sidebarCollapsed ? "lg:px-2 lg:justify-center" : "justify-start"
              )}
              onClick={() => {
                // This would open a new chat or reset current chat
                if (pathname !== '/app/dashboard') {
                  router.push('/app/dashboard');
                }
              }}
              title={sidebarCollapsed ? "Nueva Conversación" : ""}
            >
              <MessageSquare className={cn(
                "h-4 w-4 transition-all duration-300",
                sidebarCollapsed ? "" : "mr-2"
              )} />
              <span className={cn(
                "transition-all duration-300",
                sidebarCollapsed ? "lg:hidden" : ""
              )}>
                Nueva Conversación
              </span>
            </Button>
          </div>

          {/* User section */}
          <div className="border-t border-border p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3 min-w-0 flex-1">
                <Avatar className="h-8 w-8 shrink-0">
                  <AvatarFallback className="text-xs font-medium">
                    {user.email.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">
                    {user.name || user.email.split('@')[0]}
                  </p>
                  <p className="text-xs text-muted-foreground truncate">
                    {user.email}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={signOut}
                className="text-muted-foreground hover:text-foreground shrink-0"
                title="Cerrar Sesión"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className={cn(
        "transition-all duration-300",
        sidebarCollapsed ? "lg:pl-20" : "lg:pl-80"
      )}>
        {/* Top header */}
        <header className="flex h-16 items-center justify-between border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              className="lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-4 w-4" />
            </Button>
            <div>
              <h1 className="text-lg font-semibold">
                {currentPage?.name || 'Dashboard'}
              </h1>
              {currentPage?.description && (
                <p className="text-xs text-muted-foreground">
                  {currentPage.description}
                </p>
              )}
            </div>
          </div>
          
            <ThemeToggle />
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
