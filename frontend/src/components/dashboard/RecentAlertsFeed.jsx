import React from 'react';
import { ShieldAlert, AlertTriangle, AlertCircle, Info } from 'lucide-react';
import { Badge } from '../ui/Badge';

export function RecentAlertsFeed({ alerts }) {
  if (!alerts || alerts.length === 0) {
    return <div className="p-4 text-center text-textMuted font-mono text-sm">NO ACTIVE THREATS</div>;
  }

  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'critical': return 'text-error border-error/50 bg-error/10';
      case 'high': return 'text-warning border-warning/50 bg-warning/10';
      case 'medium': return 'text-info border-info/50 bg-info/10';
      default: return 'text-textMuted border-border bg-surfaceHighlight';
    }
  };

  const getSeverityIcon = (severity) => {
    switch(severity) {
      case 'critical': return <ShieldAlert size={14} className="text-error" />;
      case 'high': return <AlertTriangle size={14} className="text-warning" />;
      case 'medium': return <AlertCircle size={14} className="text-info" />;
      default: return <Info size={14} className="text-textMuted" />;
    }
  };

  return (
    <div className="divide-y divide-border/50 max-h-80 overflow-y-auto custom-scrollbar">
      {alerts.map(alert => (
        <div key={alert.id} className={`p-4 hover:bg-surfaceHighlight/50 transition-colors border-l-2 ${getSeverityColor(alert.severity).split(' ')[1]}`}>
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3">
              <div className={`p-2 rounded mt-0.5 ${getSeverityColor(alert.severity).split(' ')[2]}`}>
                {getSeverityIcon(alert.severity)}
              </div>
              <div>
                <p className="font-bold text-sm text-textMain">{alert.alert_type || 'Alert'}</p>
                <p className="text-xs text-textMuted mt-1 max-w-[250px]">{alert.message}</p>
              </div>
            </div>
            <div className="text-right">
              <Badge variant={alert.severity === 'critical' ? 'error' : alert.severity === 'high' ? 'warning' : 'info'}>
                {alert.severity.toUpperCase()}
              </Badge>
              <p className="text-[10px] text-textMuted font-mono mt-1.5 uppercase">
                NODE ID: {alert.device_id}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
