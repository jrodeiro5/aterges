// components/ui/loading-logo.tsx
'use client';

import { AtergesLogoIcon } from '@/components/ui/aterges-logo-icon';
import { cn } from '@/lib/utils';

interface LoadingLogoProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  className?: string;
}

export function LoadingLogo({ size = 'md', text, className }: LoadingLogoProps) {
  const sizeMap = {
    sm: 16,
    md: 24, 
    lg: 32
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  return (
    <div className={cn(
      "flex flex-col items-center justify-center gap-3 text-foreground",
      className
    )}>
      <AtergesLogoIcon
        size={sizeMap[size]}
        className="transition-colors"
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