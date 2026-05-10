/**
 * TeleTrack Enterprise — Alert Trend Chart
 * Line chart showing alert volume over time.
 */

import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { Card } from '../ui/Card';
import { dashboardApi } from '../../api';

export function AlertTrendChart() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        const res = await dashboardApi.getAlertTrends();
        if (res.success && res.data) {
          setData(res.data.map(d => ({
            ...d,
            date: d.date?.slice(5), // Format: MM-DD
          })));
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchTrends();
  }, []);

  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
      <div className="bg-surface border border-primary/30 rounded-lg px-3 py-2 shadow-lg">
        <p className="text-xs text-textMuted font-mono">{label}</p>
        <p className="text-sm font-bold text-primary">{payload[0].value} alerts</p>
      </div>
    );
  };

  return (
    <Card className="p-6 h-full flex flex-col">
      <h3 className="text-xs font-bold text-textMuted uppercase tracking-widest mb-4">
        Alert Trend <span className="text-primary">(30 days)</span>
      </h3>
      
      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : data.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-textMuted font-mono text-sm">
          NO TREND DATA
        </div>
      ) : (
        <div className="flex-1 min-h-0">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
              <defs>
                <linearGradient id="alertGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00f0ff" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#00f0ff" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="date"
                tick={{ fontSize: 10, fill: '#8a8d9b' }}
                axisLine={{ stroke: '#2a2d3d' }}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 10, fill: '#8a8d9b' }}
                axisLine={false}
                tickLine={false}
                allowDecimals={false}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="count"
                stroke="#00f0ff"
                strokeWidth={2}
                fill="url(#alertGradient)"
                dot={false}
                activeDot={{ r: 4, fill: '#00f0ff', stroke: '#0a0a0f', strokeWidth: 2 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}
