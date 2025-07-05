import './globals.css';
import type { Metadata, Viewport } from 'next';
import { ThemeProvider } from '@/components/theme-provider';
import { Toaster } from '@/components/ui/sonner';
import { Analytics } from '@vercel/analytics/next';
import { SpeedInsights } from '@vercel/speed-insights/next';
import { GoogleTagManager, GoogleTagManagerNoScript } from '@/components/analytics/GoogleTagManager';

export const metadata: Metadata = {
  title: 'Aterges AI - Automatización Inteligente para tu Negocio',
  description: 'Plataforma SaaS de IA para automatizar procesos empresariales, marketing digital y e-commerce.',
  keywords: 'IA, automatización, SaaS, marketing digital, e-commerce, inteligencia artificial',
  authors: [{ name: 'Aterges AI' }],
  icons: {
    icon: [
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
      { url: '/favicon.ico' }
    ],
    apple: [
      { url: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' }
    ],
    other: [
      {
        rel: 'mask-icon',
        url: '/icon0.svg',
        color: '#000000'
      }
    ]
  },
  manifest: '/site.webmanifest'
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
  const gtmId = process.env.NEXT_PUBLIC_GTM_ID;
  
  return (
    <html lang="es" suppressHydrationWarning>
      <head>
        {/* Google Tag Manager */}
        {gtmId && <GoogleTagManager gtmId={gtmId} />}
      </head>
      <body className="min-h-screen bg-background font-sans antialiased">
        {/* Google Tag Manager (noscript) */}
        {gtmId && <GoogleTagManagerNoScript gtmId={gtmId} />}
        
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem
          disableTransitionOnChange={false}
        >
          {children}
          <Toaster richColors />
          
          {/* Vercel Analytics & Speed Insights */}
          <Analytics />
          <SpeedInsights />
          
          {/* Note: GA4 tracking is handled through GTM only */}
          {/* Configure GA4 as a tag within your GTM container */}
        </ThemeProvider>
      </body>
    </html>
  );
}