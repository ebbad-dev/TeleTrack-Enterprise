import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardHeader, CardTitle } from '../ui/Card';

// Simulated traffic data
const generateData = () => {
  const data = [];
  const now = new Date();
  for (let i = 24; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 5 * 60000); // 5 min intervals
    data.push({
      time: time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      inbound: Math.floor(Math.random() * 500) + 200,
      outbound: Math.floor(Math.random() * 400) + 100,
    });
  }
  return data;
};

const data = generateData();

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-surface/90 border border-border p-3 rounded-lg shadow-[0_0_15px_rgba(0,0,0,0.5)] backdrop-blur-md">
        <p className="text-textMuted text-xs mb-2 font-mono">{label}</p>
        <div className="space-y-1">
          <p className="text-primary text-sm font-semibold neon-text">IN: {payload[0].value} Mbps</p>
          <p className="text-accent text-sm font-semibold">OUT: {payload[1].value} Mbps</p>
        </div>
      </div>
    );
  }
  return null;
};

export function TrafficChart() {
  return (
    <Card className="min-h-[300px]">
      <CardHeader>
        <CardTitle>GLOBAL BANDWIDTH TELEMETRY</CardTitle>
      </CardHeader>
      <div className="h-[250px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorIn" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00f0ff" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#00f0ff" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorOut" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#7000ff" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#7000ff" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3d" vertical={false} />
            <XAxis dataKey="time" stroke="#8a8d9b" fontSize={10} tickMargin={10} axisLine={false} tickLine={false} />
            <YAxis stroke="#8a8d9b" fontSize={10} axisLine={false} tickLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Area type="monotone" dataKey="inbound" stroke="#00f0ff" fillOpacity={1} fill="url(#colorIn)" strokeWidth={2} />
            <Area type="monotone" dataKey="outbound" stroke="#7000ff" fillOpacity={1} fill="url(#colorOut)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
