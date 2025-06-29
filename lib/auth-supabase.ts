import { supabase } from './supabase'
import { User as SupabaseUser } from '@supabase/supabase-js'

interface User {
  id: string;
  email: string;
  name?: string;
}

interface AuthResponse {
  user: User;
  token?: string;
}

class SupabaseAuthService {
  async signup(email: string, password: string): Promise<AuthResponse> {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    })

    if (error) {
      throw new Error(error.message)
    }

    if (!data.user) {
      throw new Error('Error creating user')
    }

    return {
      user: {
        id: data.user.id,
        email: data.user.email!,
        name: data.user.user_metadata?.name
      }
    }
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })

    if (error) {
      throw new Error(error.message)
    }

    if (!data.user) {
      throw new Error('Login failed')
    }

    return {
      user: {
        id: data.user.id,
        email: data.user.email!,
        name: data.user.user_metadata?.name
      }
    }
  }

  async getCurrentUser(): Promise<User | null> {
    const { data: { user } } = await supabase.auth.getUser()
    
    if (!user) return null

    return {
      id: user.id,
      email: user.email!,
      name: user.user_metadata?.name
    }
  }

  async logout(): Promise<void> {
    await supabase.auth.signOut()
    window.location.href = '/login'
  }

  isAuthenticated(): boolean {
    // This will be reactive with Supabase's auth state
    return !!supabase.auth.getSession()
  }

  getAuthHeader(): { Authorization: string } | {} {
    // Not needed with Supabase client - auth is handled automatically
    return {}
  }

  // Get the auth state change listener
  onAuthStateChange(callback: (user: User | null) => void) {
    return supabase.auth.onAuthStateChange((event, session) => {
      if (session?.user) {
        callback({
          id: session.user.id,
          email: session.user.email!,
          name: session.user.user_metadata?.name
        })
      } else {
        callback(null)
      }
    })
  }
}

export const supabaseAuthService = new SupabaseAuthService()
export type { User, AuthResponse }