import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Server, Activity, ShieldAlert, Cpu, Network, HeartPulse, Clock, Database } from 'lucide-react';
import { dashboardApi, devicesApi, alertsApi, networkApi } from '../api';
import { extractItems } from '../api/helpers';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { SystemHealthGauge } from '../components/dashboard/SystemHealthGauge';
import { SLAGauge } from '../components/dashboard/SLAGauge';
import { DeviceStatusPieChart } from '../components/dashboard/DeviceStatusPieChart';
import { AlertTrendChart } from '../components/dashboard/AlertTrendChart';
import { IncidentBreakdown } from '../components/dashboard/IncidentBreakdown';
import { RecentAlertsFeed } from '../components/dashboard/RecentAlertsFeed';
import { TrafficChart } from '../components/dashboard/TrafficChart';
import useToastStore from '../store/toastStore';

export function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Real-time feeds
  const [devices, setDevices] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [links, setLinks] = useState([]);

  const toast = useToastStore;

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [sumRes, devRes, alertRes, linkRes] = await Promise.all([
          dashboardApi.getSummary(),
          devicesApi.getDevices({ per_page: 5 }),
          alertsApi.getAlerts({ status: 'open', per_page: 5 }),
          networkApi.getLinks({ per_page: 5 })
        ]);
        
        if (sumRes.success) setSummary(sumRes.data);
        setDevices(extractItems(devRes));
        setAlerts(extractItems(alertRes));
        setLinks(extractItems(linkRes));
      } catch (error) {
        console.error('Dashboard fetch error:', error);
        toast.error('Failed to load dashboard metrics');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center space-y-4">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <div className="text-primary font-mono text-lg tracking-widest animate-pulse neon-text">INITIALIZING TELEMETRY...</div>
      </div>
    );
  }

  const kpiCards = [
    { title: "TOTAL DEVICES", value: summary?.total_devices || 0, icon: <Server size={24} />, color: "text-primary", border: "border-primary" },
    { title: "ACTIVE ALERTS", value: summary?.active_alerts || 0, icon: <ShieldAlert size={24} />, color: "text-error", border: "border-error" },
    { title: "NETWORK LINKS", value: summary?.total_links || 0, icon: <Network size={24} />, color: "text-info", border: "border-info" },
    { title: "SYSTEM UPTIME", value: "99.98%", icon: <Clock size={24} />, color: "text-success", border: "border-success" },
  ];

  return (
    <motion.div 
      className="space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-textMain tracking-wide">COMMAND <span className="text-primary neon-text">CENTER</span></h1>
          <p className="text-textMuted mt-1 font-mono text-sm uppercase">Global Infrastructure Overview</p>
        </div>
        <div className="flex items-center space-x-2 bg-surfaceHighlight/50 px-4 py-2 rounded-lg border border-border">
          <Activity size={16} className="text-success animate-pulse" />
          <span className="text-xs font-mono text-success tracking-widest">SYSTEM ONLINE</span>
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiCards.map((kpi, i) => (
          <Card key={i} className={`border-l-4 ${kpi.border} bg-surface/60 hover:bg-surfaceHighlight/50 transition-colors`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-textMuted font-mono font-semibold tracking-wider mb-1">{kpi.title}</p>
                <h3 className="text-3xl font-bold text-textMain">{kpi.value}</h3>
              </div>
              <div className={`p-3 rounded-lg bg-surfaceHighlight ${kpi.color}`}>
                {kpi.icon}
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card className="h-96 p-0 overflow-hidden flex flex-col relative">
            <div className="p-4 border-b border-border bg-surfaceHighlight/30 flex justify-between items-center z-10">
              <h3 className="text-sm font-bold text-textMain font-mono uppercase tracking-wider flex items-center">
                <Activity size={16} className="mr-2 text-primary" />
                Network Traffic Metrics
              </h3>
            </div>
            <div className="flex-1 w-full h-full relative p-4">
              <TrafficChart />
            </div>
          </Card>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="h-80">
              <AlertTrendChart />
            </Card>
            <Card className="h-80">
              <IncidentBreakdown />
            </Card>
          </div>
        </div>

        <div className="space-y-6">
          <Card className="flex flex-col items-center justify-center p-6 h-48 relative overflow-hidden group">
            <div className="absolute inset-0 bg-cyber-grid opacity-20"></div>
            <SystemHealthGauge value={summary?.healthy_devices ? Math.round((summary.healthy_devices / Math.max(1, summary.total_devices)) * 100) : 100} />
            <h3 className="mt-4 text-sm font-bold font-mono tracking-widest text-textMain z-10">INFRASTRUCTURE HEALTH</h3>
          </Card>
          
          <Card className="flex flex-col items-center justify-center p-6 h-48 relative overflow-hidden">
            <div className="absolute inset-0 bg-cyber-grid opacity-20"></div>
            <SLAGauge compliance={94.5} />
            <h3 className="mt-4 text-sm font-bold font-mono tracking-widest text-textMain z-10">SLA COMPLIANCE</h3>
          </Card>

          <Card className="h-[23rem] flex flex-col p-0">
            <div className="p-4 border-b border-border bg-surfaceHighlight/30">
              <h3 className="text-sm font-bold text-textMain font-mono uppercase tracking-wider flex items-center">
                <Database size={16} className="mr-2 text-primary" />
                Device Distribution
              </h3>
            </div>
            <div className="flex-1 p-4">
              <DeviceStatusPieChart />
            </div>
          </Card>
        </div>
      </div>

      {/* Bottom Data Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-0 overflow-hidden">
          <div className="p-4 border-b border-border bg-surfaceHighlight/30 flex justify-between items-center">
            <h3 className="text-sm font-bold text-textMain font-mono uppercase tracking-wider flex items-center">
              <ShieldAlert size={16} className="mr-2 text-error" />
              Critical Threat Feed
            </h3>
            <Badge variant="error" className="animate-pulse">{alerts.length} ACTIVE</Badge>
          </div>
          <div className="p-0">
            {alerts.length > 0 ? (
              <RecentAlertsFeed alerts={alerts} />
            ) : (
              <div className="p-8 text-center text-textMuted font-mono text-sm">NO ACTIVE THREATS DETECTED</div>
            )}
          </div>
        </Card>

        <Card className="p-0 overflow-hidden">
          <div className="p-4 border-b border-border bg-surfaceHighlight/30">
            <h3 className="text-sm font-bold text-textMain font-mono uppercase tracking-wider flex items-center">
              <Cpu size={16} className="mr-2 text-primary" />
              Resource Intensive Nodes
            </h3>
          </div>
          <div className="p-0">
            {devices.length > 0 ? (
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-textMuted uppercase bg-surfaceHighlight/10 border-b border-border">
                  <tr>
                    <th className="px-4 py-3">Node ID</th>
                    <th className="px-4 py-3">CPU</th>
                    <th className="px-4 py-3">MEM</th>
                    <th className="px-4 py-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {devices.map(dev => (
                    <tr key={dev.id} className="hover:bg-surfaceHighlight/20 transition-colors">
                      <td className="px-4 py-3 font-mono font-bold text-textMain">{dev.device_name}</td>
                      <td className="px-4 py-3">
                        <div className="flex items-center space-x-2">
                          <span className={`font-mono text-xs ${dev.cpu_usage > 80 ? 'text-error' : 'text-textMuted'}`}>{dev.cpu_usage || 0}%</span>
                          <div className="w-16 h-1.5 bg-surfaceHighlight rounded-full overflow-hidden">
                            <div className={`h-full ${dev.cpu_usage > 80 ? 'bg-error' : 'bg-primary'}`} style={{ width: `${Math.min(100, dev.cpu_usage || 0)}%` }}></div>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center space-x-2">
                          <span className={`font-mono text-xs ${dev.memory_usage > 80 ? 'text-warning' : 'text-textMuted'}`}>{dev.memory_usage || 0}%</span>
                          <div className="w-16 h-1.5 bg-surfaceHighlight rounded-full overflow-hidden">
                            <div className={`h-full ${dev.memory_usage > 80 ? 'bg-warning' : 'bg-info'}`} style={{ width: `${Math.min(100, dev.memory_usage || 0)}%` }}></div>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant={dev.status === 'online' ? 'success' : dev.status === 'offline' ? 'error' : 'warning'}>
                          {dev.status?.toUpperCase()}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-8 text-center text-textMuted font-mono text-sm">NO DEVICES REGISTERED</div>
            )}
          </div>
        </Card>
      </div>
    </motion.div>
  );
}
