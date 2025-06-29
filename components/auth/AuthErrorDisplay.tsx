'use client';

import { useState } from 'react';
import { AlertCircle, Mail, RefreshCw, CheckCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { 
  AuthError, 
  AUTH_ERRORS, 
  getAuthErrorMessage, 
  getAuthErrorHelp,
  canResendConfirmation,
  getUserEmailFromError,
  resendConfirmationEmail 
} from '@/lib/auth-utils';

interface AuthErrorDisplayProps {
  error: AuthError;
  onRetry?: () => void;
  className?: string;
}

export function AuthErrorDisplay({ error, onRetry, className }: AuthErrorDisplayProps) {
  const [isResending, setIsResending] = useState(false);
  const [resendStatus, setResendStatus] = useState<{
    type: 'success' | 'error' | null;
    message: string;
  }>({ type: null, message: '' });

  const message = getAuthErrorMessage(error);
  const helpText = getAuthErrorHelp(error);
  const canResend = canResendConfirmation(error);
  const userEmail = getUserEmailFromError(error);

  const handleResendConfirmation = async () => {
    if (!userEmail) return;

    setIsResending(true);
    setResendStatus({ type: null, message: '' });

    const result = await resendConfirmationEmail(userEmail);
    
    setResendStatus({
      type: result.success ? 'success' : 'error',
      message: result.message
    });
    setIsResending(false);
  };

  // Different styling for different error types
  const getVariant = () => {
    switch (error.error) {
      case AUTH_ERRORS.EMAIL_NOT_CONFIRMED:
        return 'default'; // Less alarming for email confirmation
      case AUTH_ERRORS.EMAIL_EXISTS:
        return 'default'; // Informational
      default:
        return 'destructive'; // Standard error styling
    }
  };

  const getIcon = () => {
    switch (error.error) {
      case AUTH_ERRORS.EMAIL_NOT_CONFIRMED:
        return <Mail className="h-4 w-4" />;
      case AUTH_ERRORS.EMAIL_EXISTS:
        return <AlertCircle className="h-4 w-4" />;
      default:
        return <AlertCircle className="h-4 w-4" />;
    }
  };

  return (
    <div className={`space-y-3 ${className}`}>
      <Alert variant={getVariant()}>
        {getIcon()}
        <AlertDescription>
          <div className="space-y-2">
            <p><strong>{message}</strong></p>
            {helpText && (
              <p className="text-sm opacity-90">{helpText}</p>
            )}
          </div>
        </AlertDescription>
      </Alert>

      {/* Email confirmation specific UI */}
      {error.error === AUTH_ERRORS.EMAIL_NOT_CONFIRMED && userEmail && (
        <div className="space-y-2">
          <div className="bg-muted p-3 rounded-lg">
            <p className="text-sm font-medium mb-1">Email confirmation required for:</p>
            <p className="text-sm text-muted-foreground">{userEmail}</p>
          </div>

          {resendStatus.type && (
            <Alert variant={resendStatus.type === 'error' ? 'destructive' : 'default'}>
              {resendStatus.type === 'success' ? (
                <CheckCircle className="h-4 w-4" />
              ) : (
                <AlertCircle className="h-4 w-4" />
              )}
              <AlertDescription>{resendStatus.message}</AlertDescription>
            </Alert>
          )}

          {canResend && (
            <Button
              onClick={handleResendConfirmation}
              disabled={isResending}
              variant="outline"
              size="sm"
              className="w-full"
            >
              {isResending && <RefreshCw className="mr-2 h-4 w-4 animate-spin" />}
              {isResending ? 'Resending...' : 'Resend confirmation email'}
            </Button>
          )}
        </div>
      )}

      {/* Email already exists - suggest login */}
      {error.error === AUTH_ERRORS.EMAIL_EXISTS && (
        <div className="flex gap-2">
          <Button variant="outline" size="sm" asChild>
            <a href="/login">Go to Login</a>
          </Button>
          <Button variant="ghost" size="sm" asChild>
            <a href="/forgot-password">Forgot Password?</a>
          </Button>
        </div>
      )}

      {/* Generic retry for other errors */}
      {onRetry && error.error !== AUTH_ERRORS.EMAIL_NOT_CONFIRMED && error.error !== AUTH_ERRORS.EMAIL_EXISTS && (
        <Button onClick={onRetry} variant="outline" size="sm">
          Try Again
        </Button>
      )}
    </div>
  );
}
