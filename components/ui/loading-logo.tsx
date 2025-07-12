// components/ui/loading-logo.tsx
'use client';

import Image from 'next/image';
import { cn } from '@/lib/utils';

interface LoadingLogoProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  className?: string;
}

export function LoadingLogo({ size = 'md', text, className }: LoadingLogoProps) {
  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-12 w-12', 
    lg: 'h-16 w-16'
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  return (
    <div className={cn(
      "flex flex-col items-center justify-center gap-3",
      className
    )}>
      <div className="relative">
        <Image
          src="/aterges_logo-removebg-preview.png"
          alt="Aterges AI"
          width={64}
          height={64}
          className={cn(
            "animate-spin",
            sizeClasses[size]
          )}
          style={{
            animationDuration: '2s',
            animationTimingFunction: 'ease-in-out',
            animationDirection: 'alternate'
          }}
        />
        <div className={cn(
          "absolute inset-0 animate-pulse rounded-full",
          sizeClasses[size]
        )} />
      </div>
      {text && (
        <p className={cn(
          "text-muted-foreground animate-pulse font-medium",
          textSizeClasses[size]
        )}>
          {text}
        </p>
      )}
    </div>
  );
}