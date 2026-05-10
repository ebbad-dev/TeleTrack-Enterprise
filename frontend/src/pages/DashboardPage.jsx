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
    { label: 'Network Health', value: `${summary?.network_health || 0}%`, icon: Activity, color: 'text-success', bg: 'bg-success/10', border: 'border-success/30' },
    { label: 'Online Nodes', value: summary?.online_devices || 0, icon: Server, color: 'text-primary', bg: 'bg-primary/10', border: 'border-primary/30' },
    { label: 'Active Threats', value: summary?.open_alerts || 0, icon: AlertTriangle, color: 'text-error', bg: 'bg-error/10', border: 'border-error/30' },
    { label: 'Open Incidents', value: summary?.open_incidents || 0, icon: Flame, color: 'text-warning', bg: 'bg-warning/10', border: 'border-warning/30' },
    { label: 'SLA Compliance', value: `${summary?.sla_compliance || 100}%`, icon: Shield, color: 'text-primary', bg: 'bg-primary/10', border: 'border-primary/30' },
    { label: 'Available Techs', value: summary?.available_technicians || 0, icon: Users, color: 'text-success', bg: 'bg-success/10', border: 'border-success/30' },
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
      className="space-y-6"
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      <motion.div variants={itemVariants}>
        <h1 className="text-3xl font-bold text-textMain tracking-wide">COMMAND <span className="text-primary neon-text">CENTER</span></h1>
        <p className="text-textMuted mt-1 font-mono text-sm uppercase">Global Infrastructure Overview</p>
      </motion.div>

      {/* Stats Row — 6 cards */}
      <motion.div variants={itemVariants} className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {stats.map((stat, i) => (
          <Card key={i} className={`relative overflow-hidden ${stat.border} hover:shadow-[0_0_20px_rgba(0,240,255,0.15)] transition-all duration-300 group`}>
            <div className={`absolute -right-4 -top-4 w-24 h-24 rounded-full blur-2xl ${stat.bg} pointer-events-none transition-transform duration-500 group-hover:scale-150`} />
            <div className="flex items-center space-x-3 relative z-10">
              <div className={`p-2.5 rounded-lg ${stat.bg} ${stat.border} border group-hover:bg-transparent transition-colors`}>
                <stat.icon size={20} className={stat.color} />
              </div>
              <div>
                <p className="text-[10px] font-bold text-textMuted uppercase tracking-widest">{stat.label}</p>
                <p className={`text-2xl font-bold ${stat.color} mt-0.5 drop-shadow-md`}>{stat.value}</p>
              </div>
            </div>
          </Card>
        ))}
      </motion.div>

      {/* Network Map + Recent Alerts */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <motion.div variants={itemVariants} className="xl:col-span-2 h-[500px]">
          <NetworkMap3D devices={devices} links={links} />
        </motion.div>
        
        <motion.div variants={itemVariants} className="h-[500px]">
          <RecentAlertsFeed alerts={alerts} />
        </motion.div>
      </div>

      {/* Analytics Row — Alert Trend + Incident Breakdown + SLA Gauge */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-2 min-h-[300px]">
          <AlertTrendChart />
        </div>
        <div className="min-h-[300px]">
          <IncidentBreakdown />
        </div>
        <div className="min-h-[300px]">
          <SLAGauge 
            compliance={summary?.sla_compliance || 100} 
            breached={summary?.sla_breached_count || 0} 
          />
        </div>
      </motion.div>

      {/* Bottom Row — Traffic Chart + Device Pie + System Health */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="min-h-[300px]">
          <TrafficChart />
        </div>
        <div className="min-h-[300px]">
          <DeviceStatusPieChart devices={devices} />
        </div>
        <div className="min-h-[300px]">
          <SystemHealthGauge summary={summary} />
        </div>
      </motion.div>
      
    </motion.div>
  );
}
