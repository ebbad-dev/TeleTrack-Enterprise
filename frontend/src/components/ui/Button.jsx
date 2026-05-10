import React from 'react';
import { cn } from './Card';

export function Button({ className, variant = 'primary', size = 'default', children, ...props }) {
  const variants = {
    primary: 'bg-primary/10 text-primary border border-primary hover:bg-primary/20 hover:shadow-[0_0_15px_rgba(0,240,255,0.4)]',
    secondary: 'bg-surfaceHighlight text-textMain border border-border hover:bg-surfaceHighlight/80',
    danger: 'bg-error/10 text-error border border-error hover:bg-error/20 hover:shadow-[0_0_15px_rgba(255,0,60,0.4)]',
    ghost: 'bg-transparent text-textMuted hover:text-primary hover:bg-primary/5',
  };

  const sizes = {
    sm: 'h-8 px-3 text-sm',
    default: 'h-10 px-4 py-2',
    lg: 'h-12 px-8 text-lg',
  };

  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-md font-medium transition-all duration-300 focus:outline-none disabled:opacity-50 disabled:pointer-events-none",
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
