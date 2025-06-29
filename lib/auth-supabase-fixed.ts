'use client';

import { createClient } from '@supabase/supabase-js';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

interface AuthUser {
  id: string;
  email: string;
  name?: string;
}

interface AuthState {
  user: AuthUser | null;
  loading: boolean;
}

class SupabaseAuthService {
  private supabase;
  
  constructor() {
    this.supabase = createClient(supabaseUrl, supabaseAnonKey);
  }

  async signUp(email: string, password: string) {
    try {
      const { data, error } = await this.supabase.auth.signUp({
        email,
        password,
        options: {
          // Redirect to production URL after email confirmation
          emailRedirectTo: `${window.location.origin}/auth/callback`,
        },
      });

      if (error) throw error;

      return {
        user: data.user,
        session: data.session,
        needsEmailConfirmation: !data.session && data.user && !data.user.email_confirmed_at,
      };
    } catch (error: any) {
      console.error('Signup error:', error);
      throw new Error(this.getErrorMessage(error));
    }
  }

  async signIn(email: string, password: string) {
    try {
      const { data, error } = await this.supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;

      return {
        user: data.user,
        session: data.session,
      };
    } catch (error: any) {
      console.error('Signin error:', error);
      throw new Error(this.getErrorMessage(error));
    }
  }

  async signOut() {
    try {
      const { error } = await this.supabase.auth.signOut();
      if (error) throw error;
    } catch (error: any) {
      console.error('Signout error:', error);
      throw new Error('Error signing out');
    }
  }

  async resendConfirmation(email: string) {
    try {
      const { error } = await this.supabase.auth.resend({
        type: 'signup',
        email,
        options: {
          emailRedirectTo: `${window.location.origin}/auth/callback`,
        },
      });

      if (error) throw error;

      return { success: true, message: 'Confirmation email sent successfully!' };
    } catch (error: any) {
      console.error('Resend confirmation error:', error);
      return { success: false, message: 'Failed to resend confirmation email' };
    }
  }

  onAuthStateChange(callback: (authState: AuthState) => void) {
    return this.supabase.auth.onAuthStateChange((event, session) => {
      console.log('Auth state changed:', event, session?.user?.email);
      callback({
        user: session?.user ? {
          id: session.user.id,
          email: session.user.email || '',
          name: session.user.user_metadata?.name,
        } : null,
        loading: false,
      });
    });
  }

  async getCurrentUser(): Promise<AuthUser | null> {
    try {
      const { data: { user }, error } = await this.supabase.auth.getUser();
      if (error) throw error;
      
      return user ? {
        id: user.id,
        email: user.email || '',
        name: user.user_metadata?.name,
      } : null;
    } catch (error) {
      console.error('Get current user error:', error);
      return null;
    }
  }

  private getErrorMessage(error: any): string {
    console.log('Full error object:', error);
    
    if (error.message?.includes('Invalid login credentials')) {
      return 'Email o contraseña incorrectos';
    }
    if (error.message?.includes('Email not confirmed')) {
      return 'Por favor confirma tu email antes de iniciar sesión';
    }
    if (error.message?.includes('User already registered')) {
      return 'Este email ya está registrado. Intenta iniciar sesión.';
    }
    if (error.message?.includes('Password should be at least 6 characters')) {
      return 'La contraseña debe tener al menos 6 caracteres';
    }
    if (error.message?.includes('Unable to validate email address') || error.message?.includes('invalid')) {
      return 'Email inválido. Usa un dominio real como @gmail.com';
    }
    if (error.message?.includes('already exists') || error.message?.includes('already registered')) {
      return 'Este email ya está registrado. Intenta iniciar sesión.';
    }
    return error.message || 'Ha ocurrido un error inesperado';
  }
}

export const supabaseAuthService = new SupabaseAuthService();
export type { AuthUser, AuthState };

// Hook for using auth in components
export function useSupabaseAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    loading: true,
  });
  const router = useRouter();

  useEffect(() => {
    // Get initial session
    supabaseAuthService.getCurrentUser().then(user => {
      setAuthState({ user, loading: false });
    });

    // Listen for auth changes
    const { data: { subscription } } = supabaseAuthService.onAuthStateChange(setAuthState);

    return () => subscription.unsubscribe();
  }, []);

  const signUp = async (email: string, password: string) => {
    try {
      const result = await supabaseAuthService.signUp(email, password);
      
      if (result.needsEmailConfirmation) {
        toast.success('¡Cuenta creada! Revisa tu email para confirmar tu cuenta.');
        return { needsEmailConfirmation: true, email };
      } else if (result.session) {
        toast.success('¡Cuenta creada y sesión iniciada!');
        router.push('/app/dashboard');
        return { needsEmailConfirmation: false, email };
      }
    } catch (error: any) {
      console.error('Signup error in hook:', error);
      toast.error(error.message);
      throw error;
    }
  };

  const signIn = async (email: string, password: string) => {
    try {
      await supabaseAuthService.signIn(email, password);
      toast.success('¡Bienvenido de vuelta!');
      router.push('/app/dashboard');
    } catch (error: any) {
      console.error('Signin error in hook:', error);
      
      // Handle specific error cases for better UX
      if (error.message.includes('Email not confirmed') || error.message.includes('confirma tu email')) {
        return { needsEmailConfirmation: true, email };
      }
      
      toast.error(error.message);
      throw error;
    }
  };

  const signOut = async () => {
    try {
      await supabaseAuthService.signOut();
      toast.success('Sesión cerrada correctamente');
      router.push('/');
    } catch (error: any) {
      toast.error(error.message);
    }
  };

  return {
    user: authState.user,
    loading: authState.loading,
    signUp,
    signIn,
    signOut,
    resendConfirmation: supabaseAuthService.resendConfirmation,
  };
}
