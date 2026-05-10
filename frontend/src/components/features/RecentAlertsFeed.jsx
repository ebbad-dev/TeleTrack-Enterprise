import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardHeader, CardTitle } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { format } from 'date-fns';

export function RecentAlertsFeed({ alerts = [] }) {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const item = {
    hidden: { opacity: 0, x: -20 },
    show: { opacity: 1, x: 0 }
  };

  return (
    <Card className="min-h-[300px] h-full overflow-hidden flex flex-col">
      <CardHeader className="pb-2 border-b border-border/50">
        <CardTitle>ACTIVE THREAT FEED</CardTitle>
      </CardHeader>
      
      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
        {alerts.length === 0 ? (
          <div className="flex items-center justify-center h-full text-textMuted font-mono">
            NO ACTIVE THREATS DETECTED
          </div>
        ) : (
          <motion.div 
            variants={container}
            initial="hidden"
            animate="show"
            className="space-y-3"
          >
            {alerts.slice(0, 10).map((alert) => (
              <motion.div 
                key={alert.id}
                variants={item}
                className="group p-3 rounded-lg bg-surfaceHighlight/30 border border-border hover:border-primary/50 transition-colors flex flex-col space-y-2 relative overflow-hidden"
              >
                {/* Glow effect on hover */}
                <div className="absolute inset-0 bg-gradient-to-r from-primary/0 via-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                
                <div className="flex items-center justify-between relative z-10">
                  <Badge variant={
                    alert.severity === 'critical' ? 'error' : 
                    alert.severity === 'high' ? 'warning' : 
                    alert.severity === 'medium' ? 'info' : 'default'
                  }>
                    {alert.severity.toUpperCase()}
                  </Badge>
                  <span className="text-xs text-textMuted font-mono">
                    {alert.alert_time ? format(new Date(alert.alert_time), 'HH:mm:ss') : '-'}
                  </span>
                </div>
                
                <div className="relative z-10">
                  <p className="text-sm font-medium text-textMain group-hover:text-primary transition-colors truncate">
                    {alert.alert_type}
                  </p>
                  <p className="text-xs text-textMuted truncate">
                    {alert.device?.device_name || `NODE-${alert.device_id}`} - {alert.message}
                  </p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </Card>
  );
}
