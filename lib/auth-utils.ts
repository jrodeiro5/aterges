// Enhanced Auth Utilities for Email Confirmation UX
// Add to: lib/auth-utils.ts

export interface AuthError {
  error: string;
  message: string;
  user_email?: string;
  can_resend?: boolean;
  help?: string;
}

export interface SignupResponse {
  user: {
    id: string;
    email: string;
    name?: string;
  };
  token?: string;
  message: string;
  email_confirmed: boolean;
  next_step: 'dashboard' | 'confirm_email';
  help?: string;
}

export interface LoginResponse {
  user: {
    id: string;
    email: string;
    name?: string;
  };
  token: string;
  message: string;
}

export const AUTH_ERRORS = {
  EMAIL_NOT_CONFIRMED: 'email_not_confirmed',
  INVALID_CREDENTIALS: 'invalid_credentials',
  EMAIL_EXISTS: 'email_exists',
  LOGIN_FAILED: 'login_failed'
} as const;

export const getAuthErrorMessage = (error: AuthError): string => {
  switch (error.error) {
    case AUTH_ERRORS.EMAIL_NOT_CONFIRMED:
      return "Please check your email and click the confirmation link before logging in.";
    case AUTH_ERRORS.INVALID_CREDENTIALS:
      return "Invalid email or password. Please check your credentials.";
    case AUTH_ERRORS.EMAIL_EXISTS:
      return "This email is already registered. Try logging in instead.";
    default:
      return error.message || "An error occurred. Please try again.";
  }
};

export const getAuthErrorHelp = (error: AuthError): string | null => {
  return error.help || null;
};

export const canResendConfirmation = (error: AuthError): boolean => {
  return error.can_resend === true;
};

export const getUserEmailFromError = (error: AuthError): string | null => {
  return error.user_email || null;
};

// API utility functions
export const resendConfirmationEmail = async (email: string): Promise<{ success: boolean; message: string }> => {
  try {
    const response = await fetch('/auth/resend-confirmation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    if (response.ok) {
      const data = await response.json();
      return { success: true, message: data.message };
    } else {
      const errorData = await response.json();
      return { success: false, message: errorData.detail || 'Failed to resend email' };
    }
  } catch (error) {
    return { success: false, message: 'Network error. Please try again.' };
  }
};

export const checkUserStatus = async (email: string): Promise<{
  exists: boolean;
  confirmed: boolean;
}> => {
  try {
    const response = await fetch('/auth/check-status', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    if (response.ok) {
      const data = await response.json();
      return { exists: data.exists, confirmed: data.confirmed };
    } else {
      return { exists: false, confirmed: false };
    }
  } catch (error) {
    return { exists: false, confirmed: false };
  }
};
