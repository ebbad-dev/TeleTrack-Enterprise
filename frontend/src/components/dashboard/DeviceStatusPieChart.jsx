import React, { useMemo } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { Card } from '../ui/Card';

const COLORS = {
  online: '#00f0ff',   // Primary Cyan
  offline: '#ff003c',  // Error Red
  warning: '#f5a623',  // Warning Orange
};

export function DeviceStatusPieChart({ devices }) {
  const data = useMemo(() => {
    if (!devices || devices.length === 0) return [];
    
    const counts = devices.reduce((acc, dev) => {
      acc[dev.status] = (acc[dev.status] || 0) + 1;
      return acc;
    }, {});

    return Object.keys(counts).map(key => ({
      name: key.toUpperCase(),
      value: counts[key],
      color: COLORS[key] || '#8884d8'
    }));
  }, [devices]);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-surface border border-border p-3 rounded-lg shadow-[0_0_15px_rgba(0,0,0,0.8)] backdrop-blur-md">
          <p className="text-textMain font-bold font-mono text-xs mb-1">{payload[0].name}</p>
          <p className="text-primary font-mono text-sm">{payload[0].value} DEVICES</p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="h-full min-h-[300px] flex flex-col relative overflow-hidden group">
      <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
      
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-bold text-textMain tracking-widest uppercase">FLEET <span className="text-primary neon-text">STATUS</span></h3>
      </div>
      
      <div className="flex-1 w-full relative">
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={5}
                dataKey="value"
                stroke="none"
              >
                {data.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.color} 
                    style={{ filter: `drop-shadow(0 0 8px ${entry.color}80)` }}
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                verticalAlign="bottom" 
                height={36} 
                iconType="circle"
                formatter={(value, entry) => <span className="text-xs font-mono text-textMuted tracking-wider">{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        ) : (
           <div className="absolute inset-0 flex items-center justify-center text-textMuted font-mono text-sm animate-pulse">
            AWAITING TELEMETRY...
           </div>
        )}
        
        {/* Center Text Overlay */}
        {data.length > 0 && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none pb-8">
            <div className="text-center">
              <p className="text-2xl font-bold text-textMain drop-shadow-[0_0_5px_rgba(0,240,255,0.5)]">{devices.length}</p>
              <p className="text-[10px] text-primary/80 font-mono tracking-widest">TOTAL</p>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
