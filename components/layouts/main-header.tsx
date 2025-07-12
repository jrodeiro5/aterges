// components/layouts/main-header.tsx
'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { 
  Menu, 
  Search, 
  User, 
  Settings, 
  BarChart3, 
  LogOut,
  CreditCard,
  HelpCircle,
  LayoutDashboard,
  Bot,
  Database
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { ThemeToggle } from '@/components/theme-toggle';
import { MainHeaderProps, NavigationItem } from '@/types/chat';
import { cn } from '@/lib/utils';

const navigationItems: NavigationItem[] = [
  {
    href: '/app/dashboard',
    label: 'Dashboard',
    description: 'Chat con IA y resumen de actividad',
    icon: LayoutDashboard
  },
  {
    href: '/app/agents',
    label: 'Agentes',
    description: 'Gestiona tus agentes de IA',
    icon: Bot
  },
  {
    href: '/app/integrations',
    label: 'Integraciones',
    description: 'Conecta tus APIs y servicios',
    icon: Database
  },
  {
    href: '/app/settings',
    label: 'Configuración',
    description: 'Perfil, seguridad y facturación',
    icon: Settings
  }
];

function NavLink({ 
  href, 
  label, 
  isActive 
}: { 
  href: string; 
  label: string; 
  isActive: boolean; 
}) {
  return (
    <Link
      href={href}
      className={cn(
        "px-3 py-2 rounded-md text-sm font-medium transition-colors duration-150",
        isActive 
          ? "bg-accent text-accent-foreground" 
          : "text-muted-foreground hover:text-foreground hover:bg-muted"
      )}
    >
      {label}
    </Link>
  );
}

function UserMenu({ user, onLogout }: { user: any; onLogout: () => void }) {
  const router = useRouter();
  
  const getInitials = (name?: string, email?: string) => {
    if (name) {
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    }
    return email?.slice(0, 2).toUpperCase() || 'U';
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="relative h-9 w-9 rounded-full">
          <Avatar className="h-8 w-8">
            <AvatarImage src={user.avatar} alt={user.name || user.email} />
            <AvatarFallback className="text-xs">
              {getInitials(user.name, user.email)}
            </AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-64" align="end" forceMount>
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium leading-none">
              {user.name || user.email?.split('@')[0] || 'Usuario'}
            </p>
            <p className="text-xs leading-none text-muted-foreground">
              {user.email}
            </p>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        
        <DropdownMenuItem onClick={() => router.push('/app/settings/account')}>
          <User className="mr-2 h-4 w-4" />
          Mi Cuenta
        </DropdownMenuItem>
        
        <DropdownMenuItem onClick={() => router.push('/app/settings/preferences')}>
          <Settings className="mr-2 h-4 w-4" />
          Preferencias
        </DropdownMenuItem>
        
        <DropdownMenuItem onClick={() => router.push('/app/settings/usage')}>
          <BarChart3 className="mr-2 h-4 w-4" />
          Uso & Límites
        </DropdownMenuItem>
        
        <DropdownMenuItem onClick={() => router.push('/app/settings/billing')}>
          <CreditCard className="mr-2 h-4 w-4" />
          Facturación
        </DropdownMenuItem>
        
        <DropdownMenuSeparator />
        
        <DropdownMenuItem onClick={() => router.push('/help')}>
          <HelpCircle className="mr-2 h-4 w-4" />
          Ayuda & Soporte
        </DropdownMenuItem>
        
        <DropdownMenuSeparator />
        
        <DropdownMenuItem onClick={onLogout} className="text-red-600 focus:text-red-600">
          <LogOut className="mr-2 h-4 w-4" />
          Cerrar Sesión
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function MobileMenu() {
  const pathname = usePathname();
  
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className="md:hidden">
          <Menu className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-64" align="start">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          return (
            <DropdownMenuItem key={item.href} asChild>
              <Link href={item.href} className="w-full">
                <div className="flex items-center gap-3">
                  {Icon && <Icon className="h-4 w-4" />}
                  <div className="flex flex-col">
                    <span className="font-medium">{item.label}</span>
                    <span className="text-xs text-muted-foreground">
                      {item.description}
                    </span>
                  </div>
                </div>
              </Link>
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export function MainHeader({ user, onSidebarToggle, onLogout }: MainHeaderProps) {
  const pathname = usePathname();
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-14 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-14 items-center justify-between px-4">
        {/* Left Section */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={onSidebarToggle}
            className="h-9 w-9"
          >
            <Menu className="h-4 w-4" />
          </Button>
          
          <Link href="/app/dashboard" className="flex items-center">
            <Image 
              src="/aterges_logo-removebg-preview.png" 
              alt="Aterges" 
              width={180} 
              height={48} 
              className="h-12 w-auto object-contain"
              priority
            />
          </Link>
        </div>

        {/* Center Section - Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1">
          {navigationItems.map((item) => (
            <NavLink
              key={item.href}
              href={item.href}
              label={item.label}
              isActive={pathname === item.href}
            />
          ))}
        </nav>

        {/* Right Section */}
        <div className="flex items-center gap-2">
          {/* Mobile Menu */}
          <MobileMenu />
          
          {/* Search Button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsSearchOpen(true)}
            className="h-9 w-9"
          >
            <Search className="h-4 w-4" />
          </Button>

          {/* Theme Toggle */}
          <ThemeToggle />

          {/* User Menu */}
          <UserMenu user={user} onLogout={onLogout} />
        </div>
      </div>
    </header>
  );
}
