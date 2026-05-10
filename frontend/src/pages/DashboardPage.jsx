import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Server, Activity, AlertTriangle, Users, Shield, Flame } from 'lucide-react';
import { dashboardApi, devicesApi, alertsApi, networkApi } from '../api';
import { Card } from '../components/ui/Card';
import { NetworkMap3D } from '../components/features/NetworkMap3D';
import { TrafficChart } from '../components/features/TrafficChart';
import { RecentAlertsFeed } from '../components/features/RecentAlertsFeed';
import { DeviceStatusPieChart } from '../components/dashboard/DeviceStatusPieChart';
import { SLAGauge } from '../components/dashboard/SLAGauge';
import { AlertTrendChart } from '../components/dashboard/AlertTrendChart';
import { IncidentBreakdown } from '../components/dashboard/IncidentBreakdown';
import { SystemHealthGauge } from '../components/dashboard/SystemHealthGauge';

export function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [devices, setDevices] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [sumRes, devRes, alertRes, linkRes] = await Promise.all([
          dashboardApi.getSummary(),
          devicesApi.getDevices(),
          alertsApi.getAlerts({ limit: 10 }),
          networkApi.getLinks()
        ]);
        
        if (sumRes.success) setSummary(sumRes.data);
        if (devRes.success) setDevices(devRes.data);
        if (alertRes.success) setAlerts(alertRes.data);
        if (linkRes.success) setLinks(linkRes.data);
        
      } catch (error) {
        console.error('Failed to load dashboard data', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();

    // Auto-refresh dashboard every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);

    // Listen for WebSocket dashboard updates
    const handleUpdate = () => fetchDashboardData();
    window.addEventListener('device_status_change', handleUpdate);
    window.addEventListener('new_alert', handleUpdate);

    return () => {
      clearInterval(interval);
      window.removeEventListener('device_status_change', handleUpdate);
      window.removeEventListener('new_alert', handleUpdate);
    };
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-4">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <div className="text-primary neon-text font-mono tracking-widest animate-pulse">
          INITIALIZING TELEMETRY...
        </div>
      </div>
    );
  }

  const stats = [
    { label: 'Network Health', value: `${summary?.network_health || 0}%`, icon: Activity, color: 'text-success', glow: 'shadow-[0_0_20px_rgba(16,185,129,0.2)]', bg: 'bg-success/5' },
    { label: 'Online Nodes', value: summary?.online_devices || 0, icon: Server, color: 'text-primary', glow: 'shadow-[0_0_20px_rgba(0,240,255,0.2)]', bg: 'bg-primary/5' },
    { label: 'Active Threats', value: summary?.open_alerts || 0, icon: AlertTriangle, color: 'text-error', glow: 'shadow-[0_0_20px_rgba(255,0,60,0.2)]', bg: 'bg-error/5' },
    { label: 'Open Incidents', value: summary?.open_incidents || 0, icon: Flame, color: 'text-warning', glow: 'shadow-[0_0_20px_rgba(255,179,0,0.2)]', bg: 'bg-warning/5' },
    { label: 'SLA Compliance', value: `${summary?.sla_compliance || 100}%`, icon: Shield, color: 'text-primary', glow: 'shadow-[0_0_20px_rgba(0,240,255,0.2)]', bg: 'bg-primary/5' },
    { label: 'Operatives', value: summary?.available_technicians || 0, icon: Users, color: 'text-success', glow: 'shadow-[0_0_20px_rgba(16,185,129,0.2)]', bg: 'bg-success/5' },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.08 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } }
  };

  return (
    <motion.div 
      className="space-y-8"
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      <motion.div variants={itemVariants} className="flex items-end justify-between">
        <div>
          <h1 className="text-4xl font-black text-textMain tracking-tighter uppercase italic">COMMAND <span className="text-primary neon-text">CENTER</span></h1>
          <p className="text-textMuted mt-1 font-mono text-xs uppercase tracking-widest flex items-center">
            <span className="w-2 h-2 bg-success rounded-full mr-2 animate-pulse" />
            Global Infrastructure Stream // Operational
          </p>
        </div>
        <div className="hidden md:block text-right font-mono text-[10px] text-textMuted uppercase">
          Latency: 12ms // Protocol: gRPC-v2<br/>
          Region: Global-Alpha-1
        </div>
      </motion.div>

      {/* Stats Row — 6 cards */}
      <motion.div variants={itemVariants} className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
        {stats.map((stat, i) => (
          <Card key={i} className={`relative group p-5 flex flex-col items-center justify-center text-center space-y-3 backdrop-blur-xl border-border/50 hover:border-primary/50 transition-all duration-500 ${stat.glow} hover:translate-y-[-4px]`}>
            <div className={`p-3 rounded-2xl ${stat.bg} border border-white/5 group-hover:scale-110 transition-transform duration-500`}>
              <stat.icon size={28} className={stat.color} />
            </div>
            <div>
              <p className={`text-3xl font-black ${stat.color} tracking-tight`}>{stat.value}</p>
              <p className="text-[10px] font-bold text-textMuted uppercase tracking-widest mt-1">{stat.label}</p>
            </div>
            {/* Animated corner decorations */}
            <div className="absolute top-0 right-0 w-8 h-8 pointer-events-none">
              <div className="absolute top-2 right-2 w-1 h-1 bg-white/20 rounded-full" />
            </div>
          </Card>
        ))}
      </motion.div>

      {/* Network Map + Recent Alerts */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <motion.div variants={itemVariants} className="xl:col-span-2 h-[550px]">
          <NetworkMap3D devices={devices} links={links} />
        </motion.div>
        
        <motion.div variants={itemVariants} className="h-[550px]">
          <RecentAlertsFeed alerts={alerts} />
        </motion.div>
      </div>

      {/* Analytics Row — Alert Trend + Incident Breakdown + SLA Gauge */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-2 min-h-[350px]">
          <AlertTrendChart />
        </div>
        <div className="min-h-[350px]">
          <IncidentBreakdown />
        </div>
        <div className="min-h-[350px]">
          <SLAGauge 
            compliance={summary?.sla_compliance || 100} 
            breached={summary?.sla_breached_count || 0} 
          />
        </div>
      </motion.div>

      {/* Bottom Row — Traffic Chart + Device Pie + System Health */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="min-h-[350px]">
          <TrafficChart />
        </div>
        <div className="min-h-[350px]">
          <DeviceStatusPieChart devices={devices} />
        </div>
        <div className="min-h-[350px]">
          <SystemHealthGauge summary={summary} />
        </div>
      </motion.div>
    </motion.div>
  );
}
