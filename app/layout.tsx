import './globals.css';
import type { Metadata, Viewport } from 'next';
import { ThemeProvider } from '@/components/theme-provider';
import { Toaster } from '@/components/ui/sonner';
import { Analytics } from '@vercel/analytics/next';

export const metadata: Metadata = {
  title: 'Aterges AI - Automatización Inteligente para tu Negocio',
  description: 'Plataforma SaaS de IA para automatizar procesos empresariales, marketing digital y e-commerce.',
  keywords: 'IA, automatización, SaaS, marketing digital, e-commerce, inteligencia artificial',
  authors: [{ name: 'Aterges AI' }],
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem
          disableTransitionOnChange={false}
        >
          {children}
          <Toaster richColors />
          <Analytics />
        </ThemeProvider>
      </body>
    </html>
  );
}