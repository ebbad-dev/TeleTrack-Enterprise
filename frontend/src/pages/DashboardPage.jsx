import React, { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Server, Activity, AlertTriangle, Users, Shield, Flame, Cpu, HardDrive, Clock, TrendingUp, TrendingDown, Zap, Radio } from 'lucide-react';
import { dashboardApi, devicesApi, alertsApi, networkApi } from '../api';
import { extractItems } from '../api/helpers';
import { Card } from '../components/ui/Card';
import { DeviceStatusPieChart } from '../components/dashboard/DeviceStatusPieChart';
import { SLAGauge } from '../components/dashboard/SLAGauge';
import { AlertTrendChart } from '../components/dashboard/AlertTrendChart';
import { IncidentBreakdown } from '../components/dashboard/IncidentBreakdown';
import { SystemHealthGauge } from '../components/dashboard/SystemHealthGauge';
import { RecentAlertsFeed } from '../components/dashboard/RecentAlertsFeed';
import { TrafficChart } from '../components/dashboard/TrafficChart';

/* ── Live Clock ──────────────────────────────────────────── */
function LiveClock() {
  const [time, setTime] = useState(new Date());
  useEffect(() => { const t = setInterval(() => setTime(new Date()), 1000); return () => clearInterval(t); }, []);
  return (
    <span className="font-mono text-xs text-primary tabular-nums tracking-wider">
      {time.toLocaleTimeString('en-US', { hour12: false })}
    </span>
  );
}

/* ── Animated Counter Hook ───────────────────────────────── */
function useAnimatedValue(target, duration = 800) {
  const [value, setValue] = useState(0);
  const prevRef = useRef(0);

  useEffect(() => {
    const from = prevRef.current;
    const to = typeof target === 'number' ? target : parseFloat(target) || 0;
    if (isNaN(to)) { setValue(target); return; }
    
    const startTime = performance.now();
    const animate = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(from + (to - from) * eased);
      setValue(current);
      if (progress < 1) requestAnimationFrame(animate);
      else prevRef.current = to;
    };
    requestAnimationFrame(animate);
  }, [target, duration]);

  return value;
}

/* ── Stat Card with animated counter ─────────────────────── */
function StatCard({ label, value, icon: Icon, color, trend, suffix = '', index = 0 }) {
  const numericValue = typeof value === 'number' ? value : null;
  const animatedVal = useAnimatedValue(numericValue ?? 0);
  const displayVal = numericValue !== null ? animatedVal : value;

  const trendColor = trend > 0 ? 'text-success' : trend < 0 ? 'text-error' : 'text-textMuted';
  const TrendIcon = trend > 0 ? TrendingUp : trend < 0 ? TrendingDown : null;

  const glowMap = {
    'text-primary': 'rgba(0,240,255,0.06)',
    'text-success': 'rgba(0,255,136,0.06)',
    'text-error': 'rgba(255,0,60,0.06)',
    'text-warning': 'rgba(255,179,0,0.06)',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay: index * 0.05, type: 'spring', stiffness: 300, damping: 25 }}
    >
      <Card className="glass-card p-4 xl:p-5 group cursor-default relative overflow-hidden">
        {/* Hover glow */}
        <div
          className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
          style={{ background: `radial-gradient(circle at 50% 120%, ${glowMap[color] || 'rgba(0,240,255,0.05)'} 0%, transparent 70%)` }}
        />
        {/* Top accent line */}
        <div className={`absolute top-0 left-3 right-3 h-[2px] rounded-full opacity-0 group-hover:opacity-60 transition-opacity duration-300 ${color === 'text-primary' ? 'bg-primary' : color === 'text-success' ? 'bg-success' : color === 'text-error' ? 'bg-error' : 'bg-warning'}`} />
        
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-3">
            <div className={`p-2 rounded-lg bg-surface border border-border/50 ${color} group-hover:border-current/30 transition-all duration-300`}>
              <Icon size={16} />
            </div>
            {TrendIcon && (
              <div className={`flex items-center space-x-0.5 text-[9px] font-mono ${trendColor}`}>
                <TrendIcon size={10} />
                <span>{Math.abs(trend)}%</span>
              </div>
            )}
          </div>
          <p className={`text-2xl font-black ${color} tabular-nums tracking-tight counter-value`}>
            {displayVal}{suffix}
          </p>
          <p className="text-[9px] font-medium text-textMuted uppercase tracking-wider mt-1.5">{label}</p>
        </div>
      </Card>
    </motion.div>
  );
}

/* ── Activity Pulse ──────────────────────────────────────── */
function ActivityPulse() {
  return (
    <div className="flex items-center gap-1.5">
      {[0, 1, 2, 3, 4].map(i => (
        <motion.div
          key={i}
          className="w-1 bg-primary rounded-full"
          animate={{ height: [4, 12 + Math.random() * 8, 4] }}
          transition={{ duration: 0.8 + i * 0.1, repeat: Infinity, ease: 'easeInOut', delay: i * 0.1 }}
        />
      ))}
    </div>
  );
}

/* ── Dashboard Page ──────────────────────────────────────── */
export function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [devices, setDevices] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sumRes, devRes, alertRes, linkRes] = await Promise.all([
          dashboardApi.getSummary(),
          devicesApi.getDevices(),
          alertsApi.getAlerts({ limit: 10 }),
          networkApi.getLinks()
        ]);
        if (sumRes.success) setSummary(sumRes.data);
        setDevices(extractItems(devRes));
        setAlerts(extractItems(alertRes));
        setLinks(extractItems(linkRes));
      } catch (err) {
        console.error('Dashboard load failed', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-4">
        <div className="relative">
          <div className="w-20 h-20 border-4 border-primary/20 rounded-full" />
          <div className="absolute inset-0 w-20 h-20 border-4 border-transparent border-t-primary rounded-full animate-spin" />
          <div className="absolute inset-2 w-16 h-16 border-2 border-transparent border-b-accent rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }} />
        </div>
        <p className="text-primary font-mono text-sm tracking-[0.3em] animate-pulse uppercase">
          Initializing Telemetry
        </p>
        <div className="flex gap-1">
          {[0,1,2].map(i => (
            <motion.div key={i} className="w-1.5 h-1.5 rounded-full bg-primary"
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1, delay: i * 0.2, repeat: Infinity }}
            />
          ))}
        </div>
      </div>
    );
  }

  const s = summary || {};
  const stats = [
    { label: 'Network Health', value: s.network_health || 0, suffix: '%', icon: Activity, color: 'text-success', trend: 2.4 },
    { label: 'Online Nodes', value: s.online_devices || 0, icon: Server, color: 'text-primary', trend: 0 },
    { label: 'Active Threats', value: s.open_alerts || 0, icon: AlertTriangle, color: 'text-error', trend: -8 },
    { label: 'Open Incidents', value: s.open_incidents || 0, icon: Flame, color: 'text-warning', trend: 0 },
    { label: 'SLA Compliance', value: s.sla_compliance || 100, suffix: '%', icon: Shield, color: 'text-primary', trend: 1.2 },
    { label: 'Avg CPU Load', value: s.avg_cpu || 0, suffix: '%', icon: Cpu, color: s.avg_cpu > 80 ? 'text-error' : 'text-success', trend: -3 },
    { label: 'Memory Usage', value: s.avg_memory || 0, suffix: '%', icon: HardDrive, color: s.avg_memory > 80 ? 'text-warning' : 'text-primary', trend: 5 },
    { label: 'Operatives', value: `${s.available_technicians || 0}/${s.total_technicians || 0}`, icon: Users, color: 'text-success', trend: 0 },
  ];

  const anim = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.04 } }
  };
  const item = {
    hidden: { opacity: 0, y: 16 },
    show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 25 } }
  };

  return (
    <motion.div className="space-y-6" variants={anim} initial="hidden" animate="show">
      {/* Header */}
      <motion.div variants={item} className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-black text-textMain tracking-tight">
            Command <span className="text-primary neon-text">Center</span>
          </h1>
          <p className="text-textMuted mt-1 font-mono text-xs uppercase tracking-widest flex items-center gap-3">
            <span className="flex items-center gap-1.5">
              <span className="status-dot status-dot-online" />
              Infrastructure Telemetry Stream
            </span>
            <span className="hidden sm:inline text-textMuted/50">|</span>
            <span className="hidden sm:flex items-center gap-1.5">
              <Radio size={10} className="text-primary animate-pulse" />
              Live
            </span>
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono text-textMuted">
          <ActivityPulse />
          <div className="flex items-center gap-1.5">
            <Clock size={12} className="text-primary" />
            <LiveClock />
          </div>
          <span className="hidden sm:inline text-textMuted/40">Region: Global-Alpha</span>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 xl:grid-cols-8 gap-3">
        {stats.map((st, i) => <StatCard key={i} {...st} index={i} />)}
      </div>

      {/* Row: Alert Trend + Recent Alerts */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <motion.div variants={item} className="xl:col-span-2 min-h-[360px]">
          <AlertTrendChart />
        </motion.div>
        <motion.div variants={item} className="min-h-[360px]">
          <RecentAlertsFeed alerts={alerts} />
        </motion.div>
      </div>

      {/* Row: Device Pie + Incident + SLA + System Health */}
      <motion.div variants={item} className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        <div className="min-h-[320px]"><DeviceStatusPieChart devices={devices} /></div>
        <div className="min-h-[320px]"><IncidentBreakdown /></div>
        <div className="min-h-[320px]"><SLAGauge compliance={s.sla_compliance || 100} breached={s.sla_breached_count || 0} /></div>
        <div className="min-h-[320px]"><SystemHealthGauge summary={s} /></div>
      </motion.div>

      {/* Row: Traffic Chart */}
      <motion.div variants={item} className="min-h-[360px]">
        <TrafficChart />
      </motion.div>
    </motion.div>
  );
}
