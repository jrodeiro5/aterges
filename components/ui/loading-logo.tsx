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
    sm: 'h-6 w-6',
    md: 'h-8 w-8', 
    lg: 'h-12 w-12'
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
      <Image
        src="/aterges_logo-removebg-preview.png"
        alt="Aterges AI"
        width={48}
        height={48}
        className={cn(
          "object-contain",
          sizeClasses[size]
        )}
      />
      {text && (
        <p className={cn(
          "text-muted-foreground font-medium",
          textSizeClasses[size]
        )}>
          {text}
        </p>
      )}
    </div>
  );
}