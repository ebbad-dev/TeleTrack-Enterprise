/**
 * TeleTrack Enterprise — Recent Alerts Feed
 * Live-updating threat intelligence feed with severity indicators.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, AlertTriangle, AlertCircle, Info, Clock } from 'lucide-react';
import { Badge } from '../ui/Badge';
import { Card } from '../ui/Card';

const SEVERITY_CONFIG = {
  critical: { icon: ShieldAlert, color: 'text-error', border: 'border-error/50', bg: 'bg-error/10', glow: 'shadow-[0_0_8px_rgba(255,0,60,0.15)]' },
  high: { icon: AlertTriangle, color: 'text-warning', border: 'border-warning/50', bg: 'bg-warning/10', glow: '' },
  medium: { icon: AlertCircle, color: 'text-info', border: 'border-info/50', bg: 'bg-info/10', glow: '' },
  low: { icon: Info, color: 'text-textMuted', border: 'border-border', bg: 'bg-surfaceHighlight', glow: '' },
};

function TimeAgo({ dateStr }) {
  if (!dateStr) return null;
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  const hrs = Math.floor(mins / 60);
  const display = hrs > 0 ? `${hrs}h ago` : mins > 0 ? `${mins}m ago` : 'Just now';
  return (
    <span className="flex items-center gap-1 text-[9px] font-mono text-textMuted/70">
      <Clock size={8} /> {display}
    </span>
  );
}

export function RecentAlertsFeed({ alerts }) {
  return (
    <Card className="p-0 h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-border/50 shrink-0">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-error/10 border border-error/20">
            <ShieldAlert size={14} className="text-error" />
          </div>
          <h3 className="text-xs font-bold text-textMuted uppercase tracking-widest">
            Threat <span className="text-error">Intel Feed</span>
          </h3>
        </div>
        {alerts?.length > 0 && (
          <span className="text-[9px] font-mono text-error bg-error/10 px-2 py-0.5 rounded-full border border-error/20">
            {alerts.length} ACTIVE
          </span>
        )}
      </div>

      {/* Feed */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {!alerts || alerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full p-8 text-center">
            <div className="w-12 h-12 rounded-full bg-success/10 border border-success/20 flex items-center justify-center mb-3">
              <ShieldAlert size={20} className="text-success" />
            </div>
            <p className="text-textMuted font-mono text-xs tracking-widest">ALL CLEAR</p>
            <p className="text-textMuted/50 text-[10px] font-mono mt-1">No active threats detected</p>
          </div>
        ) : (
          <div className="divide-y divide-border/30">
            {alerts.map((alert, idx) => {
              const config = SEVERITY_CONFIG[alert.severity] || SEVERITY_CONFIG.low;
              const Icon = config.icon;
              return (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className={`px-5 py-3.5 hover:bg-surfaceHighlight/50 transition-all cursor-default border-l-2 ${config.border} group`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      <div className={`p-1.5 rounded-lg ${config.bg} shrink-0 mt-0.5 ${config.glow}`}>
                        <Icon size={12} className={config.color} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-sm text-textMain group-hover:text-primary transition-colors truncate">
                          {alert.alert_type || 'System Alert'}
                        </p>
                        <p className="text-xs text-textMuted mt-0.5 line-clamp-2 leading-relaxed">
                          {alert.message}
                        </p>
                        <div className="flex items-center gap-3 mt-1.5">
                          <span className="text-[9px] font-mono text-textMuted/60 uppercase">
                            NODE {alert.device_id}
                          </span>
                          <TimeAgo dateStr={alert.alert_time || alert.created_at} />
                        </div>
                      </div>
                    </div>
                    <Badge
                      variant={alert.severity === 'critical' ? 'error' : alert.severity === 'high' ? 'warning' : 'info'}
                    >
                      {alert.severity?.toUpperCase()}
                    </Badge>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </Card>
  );
}
