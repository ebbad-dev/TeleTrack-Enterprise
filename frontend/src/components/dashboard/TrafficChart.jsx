import React from 'react';

// Placeholder chart for the dashboard
export function TrafficChart() {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center text-textMuted bg-surface/50 rounded-lg border border-border overflow-hidden relative">
      <div className="absolute inset-0 bg-cyber-grid opacity-10"></div>
      <div className="absolute bottom-0 left-0 right-0 h-1/2 bg-gradient-to-t from-primary/10 to-transparent"></div>
      
      {/* Decorative chart lines */}
      <svg className="absolute inset-0 w-full h-full opacity-30" preserveAspectRatio="none">
        <path 
          d="M0,80 Q20,20 40,60 T80,40 T120,70 T160,30 T200,90" 
          vectorEffect="non-scaling-stroke" 
          fill="none" 
          stroke="var(--primary)" 
          strokeWidth="2" 
        />
        <path 
          d="M0,90 Q20,40 40,80 T80,50 T120,80 T160,40 T200,100" 
          vectorEffect="non-scaling-stroke" 
          fill="none" 
          stroke="var(--info)" 
          strokeWidth="2" 
        />
      </svg>
      
      <p className="font-mono text-sm tracking-widest z-10 neon-text opacity-50 uppercase mt-auto mb-8">
        Live telemetry stream active
      </p>
    </div>
  );
}
