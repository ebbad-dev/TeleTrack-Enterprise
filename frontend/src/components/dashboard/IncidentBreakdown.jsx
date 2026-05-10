/**
 * TeleTrack Enterprise — Incident Breakdown Chart
 * Pie/donut chart showing incidents by severity.
 */

import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { Card } from '../ui/Card';
import { dashboardApi } from '../../api';

const SEVERITY_COLORS = {
  critical: '#ff003c',
  high: '#ff6b3c',
  medium: '#ffb300',
  low: '#00ff66',
};

export function IncidentBreakdown() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await dashboardApi.getIncidentsBySeverity();
        if (res.success && res.data) {
          setData(res.data.map(d => ({
            ...d,
            name: d.severity?.charAt(0).toUpperCase() + d.severity?.slice(1),
            fill: SEVERITY_COLORS[d.severity] || '#8a8d9b',
          })));
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const total = data.reduce((sum, d) => sum + d.count, 0);

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;
    const entry = payload[0];
    return (
      <div className="bg-surface border border-border rounded-lg px-3 py-2 shadow-lg">
        <p className="text-sm font-bold" style={{ color: entry.payload.fill }}>
          {entry.name}: {entry.value}
        </p>
      </div>
    );
  };

  return (
    <Card className="p-6 flex flex-col items-center h-full">
      <h3 className="text-xs font-bold text-textMuted uppercase tracking-widest mb-4 self-start">
        Active Incidents
      </h3>

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : total === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-success font-mono text-sm">
          <span className="text-4xl mb-2">✓</span>
          NO ACTIVE INCIDENTS
        </div>
      ) : (
        <>
          <div className="relative w-40 h-40">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={65}
                  paddingAngle={3}
                  dataKey="count"
                  strokeWidth={0}
                >
                  {data.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} style={{ filter: `drop-shadow(0 0 4px ${entry.fill}40)` }} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-2xl font-bold text-textMain">{total}</span>
              <span className="text-[10px] text-textMuted font-mono">ACTIVE</span>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-3 justify-center">
            {data.map((d, i) => (
              <div key={i} className="flex items-center space-x-1.5">
                <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: d.fill }} />
                <span className="text-xs text-textMuted font-mono">{d.name} ({d.count})</span>
              </div>
            ))}
          </div>
        </>
      )}
    </Card>
  );
}
