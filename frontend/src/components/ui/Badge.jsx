import React from 'react';
import { cn } from './Card';

export function Badge({ className, variant = 'default', children, ...props }) {
  const variants = {
    default: 'bg-surfaceHighlight text-textMain border border-border',
    success: 'bg-success/10 text-success border border-success/30 shadow-[0_0_10px_rgba(0,255,102,0.2)]',
    warning: 'bg-warning/10 text-warning border border-warning/30 shadow-[0_0_10px_rgba(255,179,0,0.2)]',
    error: 'bg-error/10 text-error border border-error/30 shadow-[0_0_10px_rgba(255,0,60,0.2)]',
    info: 'bg-primary/10 text-primary border border-primary/30 shadow-[0_0_10px_rgba(0,240,255,0.2)]',
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
