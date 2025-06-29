"use client"

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { PublicLayout } from '@/components/layouts/public-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { authService } from '@/lib/auth';
import { toast } from 'sonner';
import { Loader2, Mail, Lock, User } from 'lucide-react';
import { EmailConfirmationPending } from '@/components/auth/EmailConfirmationPending';
import { AuthErrorDisplay } from '@/components/auth/AuthErrorDisplay';
import { AuthError } from '@/lib/auth-utils';

export default function SignupPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [needsConfirmation, setNeedsConfirmation] = useState(false);
  const [authError, setAuthError] = useState<AuthError | null>(null);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Clear previous errors
    setAuthError(null);
    
    if (password !== confirmPassword) {
      toast.error('Las contraseñas no coinciden');
      return;
    }

    if (password.length < 6) {
      toast.error('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    setIsLoading(true);

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        
        if (data.next_step === 'dashboard') {
          // User can login immediately (email confirmed)
          localStorage.setItem('token', data.token);
          toast.success(data.message);
          router.push('/app/dashboard');
        } else if (data.next_step === 'confirm_email') {
          // Show email confirmation screen
          setNeedsConfirmation(true);
          toast.success(data.message);
        }
      } else {
        const errorData = await response.json();
        
        if (typeof errorData.detail === 'object') {
          // Handle structured error response
          setAuthError(errorData.detail as AuthError);
        } else {
          // Handle simple error string
          toast.error(errorData.detail || 'Error al crear la cuenta');
        }
      }
    } catch (error) {
      toast.error('Error de conexión. Por favor, inténtalo de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  // Show email confirmation screen if needed
  if (needsConfirmation) {
    return (
      <EmailConfirmationPending 
        email={email} 
        onGoBack={() => setNeedsConfirmation(false)} 
      />
    );
  }

  return (
    <PublicLayout>
      <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center py-12 px-4">
        <Card className="w-full max-w-md animate-slide-up">
          <CardHeader className="space-y-1 text-center">
            <CardTitle className="text-2xl font-bold">Crea tu Cuenta</CardTitle>
            <CardDescription>
              Comienza tu transformación digital con Aterges AI
            </CardDescription>
          </CardHeader>
          <CardContent>
            {authError && (
              <div className="mb-4">
                <AuthErrorDisplay 
                  error={authError} 
                  onRetry={() => setAuthError(null)} 
                />
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Correo Electrónico</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="tu@empresa.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="password">Contraseña</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="Mínimo 6 caracteres"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-10"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirmar Contraseña</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="Repite tu contraseña"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="pl-10"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full" 
                disabled={isLoading || !email || !password || !confirmPassword}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creando Cuenta...
                  </>
                ) : (
                  'Crear Cuenta'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center text-sm">
              <span className="text-muted-foreground">¿Ya tienes una cuenta? </span>
              <Link 
                href="/login" 
                className="text-primary hover:underline font-medium"
              >
                Inicia sesión aquí
              </Link>
            </div>

            <div className="mt-4 text-center">
              <p className="text-xs text-muted-foreground">
                Al registrarte, aceptas nuestros términos de servicio y política de privacidad.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </PublicLayout>
  );
}