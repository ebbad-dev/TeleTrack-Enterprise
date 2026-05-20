/**
 * TeleTrack Enterprise — Network Traffic Chart
 * Dual-area chart showing inbound/outbound bandwidth over time.
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts';
import { Card } from '../ui/Card';
import { Wifi, ArrowUpRight, ArrowDownLeft } from 'lucide-react';

function generateTrafficData() {
  const hours = 24;
  const data = [];
  const now = new Date();
  for (let i = hours; i >= 0; i--) {
    const t = new Date(now - i * 3600000);
    const hourOfDay = t.getHours();
    // Simulate realistic traffic patterns (higher during business hours)
    const base = hourOfDay >= 8 && hourOfDay <= 18 ? 60 : 25;
    const variance = hourOfDay >= 8 && hourOfDay <= 18 ? 30 : 15;
    data.push({
      time: t.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
      inbound: Math.round(base + Math.random() * variance + Math.sin(i / 3) * 10),
      outbound: Math.round((base * 0.7) + Math.random() * (variance * 0.8) + Math.cos(i / 4) * 8),
    });
  }
  return data;
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-surface border border-primary/30 rounded-lg px-4 py-3 shadow-lg backdrop-blur-xl">
      <p className="text-[10px] text-textMuted font-mono mb-2 uppercase tracking-wider">{label}</p>
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <ArrowDownLeft size={12} className="text-primary" />
          <span className="text-sm font-bold text-primary font-mono">{payload[0]?.value} Gbps</span>
          <span className="text-[10px] text-textMuted">IN</span>
        </div>
        <div className="flex items-center gap-2">
          <ArrowUpRight size={12} className="text-accent" />
          <span className="text-sm font-bold text-accent font-mono">{payload[1]?.value} Gbps</span>
          <span className="text-[10px] text-textMuted">OUT</span>
        </div>
      </div>
    </div>
  );
};

export function TrafficChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    setData(generateTrafficData());
    const interval = setInterval(() => setData(generateTrafficData()), 30000);
    return () => clearInterval(interval);
  }, []);

  const { totalIn, totalOut, peakIn } = useMemo(() => {
    if (!data.length) return { totalIn: 0, totalOut: 0, peakIn: 0 };
    const totalIn = data.reduce((s, d) => s + d.inbound, 0);
    const totalOut = data.reduce((s, d) => s + d.outbound, 0);
    const peakIn = Math.max(...data.map(d => d.inbound));
    return { totalIn, totalOut, peakIn };
  }, [data]);

  return (
    <Card className="p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-primary/10 border border-primary/20">
            <Wifi size={14} className="text-primary" />
          </div>
          <h3 className="text-xs font-bold text-textMuted uppercase tracking-widest">
            Network <span className="text-primary">Throughput</span>
          </h3>
        </div>
        <div className="flex items-center gap-4 text-[10px] font-mono text-textMuted">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-primary" />
            Inbound
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-accent" />
            Outbound
          </span>
        </div>
      </div>

      {/* Stats strip */}
      <div className="flex items-center gap-6 mb-4 pb-3 border-b border-border/50">
        <div>
          <p className="text-[9px] font-mono text-textMuted uppercase tracking-wider">Avg Inbound</p>
          <p className="text-lg font-black text-primary font-mono tabular-nums">
            {data.length ? Math.round(totalIn / data.length) : 0}
            <span className="text-xs text-textMuted ml-1">Gbps</span>
          </p>
        </div>
        <div>
          <p className="text-[9px] font-mono text-textMuted uppercase tracking-wider">Avg Outbound</p>
          <p className="text-lg font-black text-accent font-mono tabular-nums">
            {data.length ? Math.round(totalOut / data.length) : 0}
            <span className="text-xs text-textMuted ml-1">Gbps</span>
          </p>
        </div>
        <div>
          <p className="text-[9px] font-mono text-textMuted uppercase tracking-wider">Peak</p>
          <p className="text-lg font-black text-warning font-mono tabular-nums">
            {peakIn}
            <span className="text-xs text-textMuted ml-1">Gbps</span>
          </p>
        </div>
      </div>

      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
            <defs>
              <linearGradient id="inboundGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00f0ff" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#00f0ff" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="outboundGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 6" stroke="rgba(255,255,255,0.03)" />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 9, fill: '#7d8590', fontFamily: 'JetBrains Mono, monospace' }}
              axisLine={{ stroke: '#21262d' }}
              tickLine={false}
              interval={4}
            />
            <YAxis
              tick={{ fontSize: 9, fill: '#7d8590', fontFamily: 'JetBrains Mono, monospace' }}
              axisLine={false}
              tickLine={false}
              allowDecimals={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="inbound"
              stroke="#00f0ff"
              strokeWidth={2}
              fill="url(#inboundGrad)"
              dot={false}
              activeDot={{ r: 4, fill: '#00f0ff', stroke: '#0a0a0f', strokeWidth: 2 }}
            />
            <Area
              type="monotone"
              dataKey="outbound"
              stroke="#7c3aed"
              strokeWidth={1.5}
              fill="url(#outboundGrad)"
              dot={false}
              activeDot={{ r: 3, fill: '#7c3aed', stroke: '#0a0a0f', strokeWidth: 2 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
