'use client';

import { useState } from 'react';
import { Mail, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { supabaseAuthService } from '@/lib/auth-supabase-fixed';

interface EmailConfirmationPendingProps {
  email: string;
  onGoBack?: () => void;
}

export function EmailConfirmationPending({ email, onGoBack }: EmailConfirmationPendingProps) {
  const [isResending, setIsResending] = useState(false);
  const [resendStatus, setResendStatus] = useState<{
    type: 'success' | 'error' | null;
    message: string;
  }>({ type: null, message: '' });

  const handleResendEmail = async () => {
    setIsResending(true);
    setResendStatus({ type: null, message: '' });

    const result = await supabaseAuthService.resendConfirmation(email);
    
    setResendStatus({
      type: result.success ? 'success' : 'error',
      message: result.message
    });
    setIsResending(false);
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
            <Mail className="w-6 h-6 text-blue-600" />
          </div>
          <CardTitle>Check Your Email</CardTitle>
          <CardDescription>
            We've sent a confirmation link to <strong>{email}</strong>
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert>
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>
              <strong>Account created successfully!</strong> Click the confirmation link in your email to complete your registration and login.
            </AlertDescription>
          </Alert>

          <div className="bg-muted p-4 rounded-lg">
            <h4 className="font-medium mb-2">Next steps:</h4>
            <ol className="text-sm text-muted-foreground space-y-1">
              <li>1. Check your email inbox</li>
              <li>2. Look for an email from Aterges</li>
              <li>3. Click the confirmation link</li>
              <li>4. Return here to login</li>
            </ol>
          </div>

          <div className="text-sm text-muted-foreground">
            <p>Didn't receive the email?</p>
            <ul className="mt-1 space-y-1">
              <li>• Check your spam/junk folder</li>
              <li>• Make sure you entered the correct email</li>
              <li>• Try resending the confirmation email</li>
            </ul>
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

          <div className="space-y-2">
            <Button
              onClick={handleResendEmail}
              disabled={isResending}
              variant="outline"
              className="w-full"
            >
              {isResending && <RefreshCw className="mr-2 h-4 w-4 animate-spin" />}
              {isResending ? 'Resending...' : 'Resend confirmation email'}
            </Button>

            {onGoBack && (
              <Button onClick={onGoBack} variant="ghost" className="w-full">
                Back to signup
              </Button>
            )}
          </div>

          <div className="text-center">
            <p className="text-sm text-muted-foreground">
              Already confirmed?{' '}
              <a href="/login" className="text-primary hover:underline">
                Try logging in
              </a>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
