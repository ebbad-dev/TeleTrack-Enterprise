/**
 * TeleTrack Enterprise — System Health Gauge
 * Shows overall system health metrics (avg CPU, memory, uptime).
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Cpu, HardDrive, Thermometer } from 'lucide-react';
import { Card } from '../ui/Card';

function MiniGauge({ value, label, icon: Icon, color, maxValue = 100 }) {
  const pct = Math.min(100, (value / maxValue) * 100);
  const barColor = pct > 85 ? '#ff003c' : pct > 65 ? '#ffb300' : color;

  return (
    <div className="flex items-center space-x-3 py-2.5">
      <div className="p-2 rounded-lg bg-surface border border-border">
        <Icon size={16} style={{ color: barColor }} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-textMuted font-mono uppercase">{label}</span>
          <span className="text-xs font-bold" style={{ color: barColor }}>
            {value.toFixed(1)}%
          </span>
        </div>
        <div className="w-full h-1.5 bg-border rounded-full overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{ backgroundColor: barColor }}
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
        </div>
      </div>
    </div>
  );
}

export function SystemHealthGauge({ summary }) {
  const avgCpu = summary?.avg_cpu || 0;
  const avgMemory = summary?.avg_memory || 0;
  const networkHealth = summary?.network_health || 0;

  // Overall health score (weighted average)
  const healthScore = Math.round(
    networkHealth * 0.5 +
    (100 - avgCpu) * 0.25 +
    (100 - avgMemory) * 0.25
  );

  const getHealthColor = () => {
    if (healthScore >= 85) return '#00ff66';
    if (healthScore >= 60) return '#ffb300';
    return '#ff003c';
  };

  const getHealthLabel = () => {
    if (healthScore >= 85) return 'EXCELLENT';
    if (healthScore >= 60) return 'MODERATE';
    return 'CRITICAL';
  };

  return (
    <Card className="p-6 relative overflow-hidden">
      <div
        className="absolute -left-6 -bottom-6 w-32 h-32 rounded-full blur-3xl pointer-events-none"
        style={{ backgroundColor: `${getHealthColor()}10` }}
      />

      <h3 className="text-xs font-bold text-textMuted uppercase tracking-widest mb-1">
        System Health
      </h3>
      <div className="flex items-baseline space-x-2 mb-4">
        <span className="text-4xl font-bold" style={{ color: getHealthColor() }}>
          {healthScore}
        </span>
        <span className="text-xs font-mono" style={{ color: getHealthColor() }}>
          {getHealthLabel()}
        </span>
      </div>

      <div className="space-y-1 divide-y divide-border/30">
        <MiniGauge value={avgCpu} label="Avg CPU" icon={Cpu} color="#00f0ff" />
        <MiniGauge value={avgMemory} label="Avg Memory" icon={HardDrive} color="#7000ff" />
        <MiniGauge value={100 - networkHealth} label="Downtime" icon={Thermometer} color="#ff003c" />
      </div>
    </Card>
  );
}
