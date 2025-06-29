'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { createClient } from '@supabase/supabase-js';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// Component that uses useSearchParams - needs to be wrapped in Suspense
function AuthCallbackContent() {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const [debugInfo, setDebugInfo] = useState<string>('');
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        const supabase = createClient(supabaseUrl, supabaseAnonKey);
        
        // Debug: Log all URL parameters
        const allParams = Array.from(searchParams.entries());
        const debugString = `URL Params: ${JSON.stringify(Object.fromEntries(allParams))}`;
        console.log('Auth callback debug:', debugString);
        setDebugInfo(debugString);
        
        // Get the code from URL parameters
        const code = searchParams.get('code');
        const error = searchParams.get('error');
        const error_description = searchParams.get('error_description');

        // Debug: Check what we got
        console.log('Auth callback params:', { code, error, error_description });

        if (error) {
          console.error('Auth callback error:', error, error_description);
          setStatus('error');
          setMessage(error_description || 'Error during authentication');
          return;
        }

        if (code) {
          console.log('Found code, attempting to exchange for session...');
          
          // Exchange the code for a session
          const { data, error: sessionError } = await supabase.auth.exchangeCodeForSession(code);
          
          if (sessionError) {
            console.error('Session exchange error:', sessionError);
            setStatus('error');
            setMessage('Failed to confirm email. Please try again.');
            return;
          }

          if (data.session && data.user) {
            console.log('Email confirmation successful:', data.user.email);
            setStatus('success');
            setMessage('Email confirmed successfully! Redirecting to dashboard...');
            
            // Show success message
            toast.success('¡Email confirmado! Bienvenido a Aterges AI');
            
            // Redirect to dashboard after a short delay
            setTimeout(() => {
              router.push('/app/dashboard');
            }, 2000);
          } else {
            setStatus('error');
            setMessage('No session created after email confirmation');
          }
        } else {
          // Check if this might be a direct access without confirmation
          const currentUrl = window.location.href;
          console.log('No code found. Current URL:', currentUrl);
          
          setStatus('error');
          setMessage('No confirmation code found in URL');
        }
      } catch (error) {
        console.error('Auth callback error:', error);
        setStatus('error');
        setMessage('An unexpected error occurred during email confirmation');
      }
    };

    handleAuthCallback();
  }, [searchParams, router]);

  const handleRetry = () => {
    router.push('/login');
  };

  const handleGoToDashboard = () => {
    router.push('/app/dashboard');
  };

  const handleDebugInfo = () => {
    const currentUrl = window.location.href;
    const hash = window.location.hash;
    alert(`Debug Info:\nCurrent URL: ${currentUrl}\nHash: ${hash}\nSearch Params: ${debugInfo}`);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 w-12 h-12 rounded-full flex items-center justify-center">
            {status === 'loading' && (
              <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center">
                <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
              </div>
            )}
            {status === 'success' && (
              <div className="bg-green-100 w-12 h-12 rounded-full flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
            )}
            {status === 'error' && (
              <div className="bg-red-100 w-12 h-12 rounded-full flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
            )}
          </div>
          
          <CardTitle className="text-2xl font-bold">
            {status === 'loading' && 'Confirmando Email...'}
            {status === 'success' && '¡Email Confirmado!'}
            {status === 'error' && 'Error de Confirmación'}
          </CardTitle>
          
          <CardDescription>
            {status === 'loading' && 'Por favor espera mientras confirmamos tu email'}
            {status === 'success' && 'Tu cuenta ha sido activada exitosamente'}
            {status === 'error' && 'Hubo un problema confirmando tu email'}
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-4">
          <div className="text-center">
            <p className="text-sm text-muted-foreground">
              {message}
            </p>
          </div>
          
          {status === 'success' && (
            <div className="space-y-2">
              <p className="text-sm text-center text-muted-foreground">
                Serás redirigido automáticamente en unos segundos...
              </p>
              <Button onClick={handleGoToDashboard} className="w-full">
                Ir al Dashboard
              </Button>
            </div>
          )}
          
          {status === 'error' && (
            <div className="space-y-2">
              <Button onClick={handleRetry} className="w-full">
                Intentar Iniciar Sesión
              </Button>
              <Button 
                variant="outline" 
                className="w-full" 
                onClick={() => router.push('/signup')}
              >
                Crear Nueva Cuenta
              </Button>
              <Button 
                variant="ghost" 
                size="sm"
                className="w-full text-xs"
                onClick={handleDebugInfo}
              >
                Mostrar Info de Debug
              </Button>
            </div>
          )}
          
          {status === 'loading' && (
            <div className="text-center">
              <div className="animate-pulse">
                <div className="h-4 bg-muted rounded w-3/4 mx-auto"></div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Fallback component for the Suspense boundary
function AuthCallbackFallback() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 w-12 h-12 rounded-full flex items-center justify-center">
            <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center">
              <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold">Loading...</CardTitle>
          <CardDescription>
            Processing authentication callback
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center">
            <div className="animate-pulse">
              <div className="h-4 bg-muted rounded w-3/4 mx-auto"></div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Main component that wraps the content in Suspense
export default function AuthCallbackPage() {
  return (
    <Suspense fallback={<AuthCallbackFallback />}>
      <AuthCallbackContent />
    </Suspense>
  );
}
