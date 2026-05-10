/**
 * TeleTrack Enterprise — SLA Gauge Component
 * Circular gauge showing SLA compliance percentage.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Card } from '../ui/Card';

export function SLAGauge({ compliance = 100, breached = 0 }) {
  const radius = 58;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (compliance / 100) * circumference;

  const getColor = () => {
    if (compliance >= 95) return '#00ff66';
    if (compliance >= 80) return '#ffb300';
    return '#ff003c';
  };

  return (
    <Card className="p-6 flex flex-col items-center justify-center relative overflow-hidden">
      <div className="absolute -right-6 -top-6 w-32 h-32 rounded-full blur-3xl bg-success/5 pointer-events-none" />
      <h3 className="text-xs font-bold text-textMuted uppercase tracking-widest mb-4">SLA Compliance</h3>
      
      <div className="relative w-36 h-36">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 140 140">
          {/* Background circle */}
          <circle
            cx="70" cy="70" r={radius}
            stroke="currentColor"
            className="text-border"
            strokeWidth="8"
            fill="none"
          />
          {/* Progress circle */}
          <motion.circle
            cx="70" cy="70" r={radius}
            stroke={getColor()}
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            style={{ filter: `drop-shadow(0 0 6px ${getColor()}50)` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold" style={{ color: getColor() }}>
            {compliance}%
          </span>
          <span className="text-[10px] text-textMuted font-mono uppercase">COMPLIANT</span>
        </div>
      </div>

      {breached > 0 && (
        <div className="mt-3 px-3 py-1 bg-error/10 border border-error/30 rounded-full text-xs text-error font-mono">
          {breached} SLA{breached > 1 ? 's' : ''} BREACHED
        </div>
      )}
    </Card>
  );
}
