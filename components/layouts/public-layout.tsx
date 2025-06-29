import { ReactNode } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/theme-toggle';

interface PublicLayoutProps {
  children: ReactNode;
}

export function PublicLayout({ children }: PublicLayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex h-24 items-center justify-between">
          <Link href="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
            <Image
              src="/aterges_logo-removebg-preview.png"
              alt="Aterges AI"
              width={320}
              height={85}
              className="h-20 w-auto object-contain"
              priority
              style={{ objectPosition: 'left center' }}
            />
          </Link>
          
          <div className="flex items-center space-x-3">
            <ThemeToggle />
            <div className="flex items-center space-x-2">
              <Button variant="ghost" asChild className="text-sm">
                <Link href="/login">Iniciar Sesión</Link>
              </Button>
              <Button asChild className="text-sm">
                <Link href="/signup">Registrarse</Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1">
        {children}
      </main>

      <footer className="border-t border-border/40 bg-muted/50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <div className="flex items-center space-x-2">
              <Image
                src="/aterges_logo-removebg-preview.png"
                alt="Aterges AI"
                width={240}
                height={64}
                className="h-16 w-auto opacity-80 object-contain"
                style={{ objectPosition: 'left center' }}
              />
            </div>
            <p className="text-sm text-muted-foreground text-center">
              © 2024 Aterges AI. Todos los derechos reservados.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}