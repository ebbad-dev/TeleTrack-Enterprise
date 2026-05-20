import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { databaseApi } from '../api';
import { Database, Eye, Zap, Search, Settings } from 'lucide-react';
import { Badge } from '../components/ui/Badge';

export function DatabaseStatsPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({
    activeDevices: [],
    criticalAlerts: [],
    openIncidents: [],
    triggerHistory: [],
    procedureStats: {},
    indexes: []
  });
  
  const [activeTab, setActiveTab] = useState('views');

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      try {
        const [
          activeDevices,
          criticalAlerts,
          openIncidents,
          triggerHistory,
          procedureStats,
          indexes
        ] = await Promise.all([
          databaseApi.getActiveDevicesView(),
          databaseApi.getCriticalAlertsView(),
          databaseApi.getOpenIncidentsView(),
          databaseApi.getTriggerHistory(),
          databaseApi.getProcedureStats(),
          databaseApi.getIndexes()
        ]);
        
        setData({
          activeDevices: activeDevices.data || [],
          criticalAlerts: criticalAlerts.data || [],
          openIncidents: openIncidents.data || [],
          triggerHistory: triggerHistory.data || [],
          procedureStats: procedureStats.data || {},
          indexes: indexes.data || []
        });
      } catch (error) {
        console.error("Failed to load DB stats", error);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  const tabs = [
    { id: 'views', label: 'SQL Views', icon: Eye },
    { id: 'triggers', label: 'Triggers (History)', icon: Zap },
    { id: 'procedures', label: 'Procedures (Complex Query)', icon: Settings },
    { id: 'indexes', label: 'Indexes', icon: Search }
  ];

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="w-12 h-12 border-3 border-primary/30 border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <motion.div className="space-y-6" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="flex items-center gap-3 border-b border-border pb-4">
        <div className="p-3 bg-primary/10 rounded-xl border border-primary/30">
          <Database size={24} className="text-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-black text-textMain tracking-tight">
            Database <span className="text-primary neon-text">Explorer</span>
          </h1>
          <p className="text-textMuted text-xs uppercase tracking-widest font-mono mt-1">
            Views • Triggers • Procedures • Indexes
          </p>
        </div>
      </div>

      <div className="flex gap-2 border-b border-border pb-4 overflow-x-auto">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-mono uppercase tracking-wider transition-all whitespace-nowrap
              ${activeTab === tab.id ? 'bg-primary/20 border border-primary text-primary' : 'bg-surface border border-border text-textMuted hover:border-primary/50'}`}
          >
            <tab.icon size={16} />
            {tab.label}
          </button>
        ))}
      </div>

      <div className="glass-panel p-6">
        {activeTab === 'views' && (
          <div className="space-y-8">
            <div>
              <h3 className="text-lg font-bold text-textMain mb-4 flex items-center gap-2">
                <span className="text-primary">&gt;</span> view_active_devices ({data.activeDevices.length})
              </h3>
              <div className="overflow-x-auto bg-background rounded-lg border border-border">
                <table className="w-full text-sm text-left">
                  <thead className="bg-surface text-textMuted font-mono text-xs uppercase">
                    <tr>
                      <th className="px-4 py-3">Device Name</th>
                      <th className="px-4 py-3">Type</th>
                      <th className="px-4 py-3">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.activeDevices.slice(0, 10).map((d, i) => (
                      <tr key={i} className="border-b border-border/50 hover:bg-surface/50">
                        <td className="px-4 py-3 text-textMain font-medium">{d.device_name}</td>
                        <td className="px-4 py-3 text-textMuted">{d.device_type}</td>
                        <td className="px-4 py-3"><Badge status={d.status} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-bold text-textMain mb-4 flex items-center gap-2">
                <span className="text-primary">&gt;</span> view_critical_alerts ({data.criticalAlerts.length})
              </h3>
              <div className="overflow-x-auto bg-background rounded-lg border border-border">
                <table className="w-full text-sm text-left">
                  <thead className="bg-surface text-textMuted font-mono text-xs uppercase">
                    <tr>
                      <th className="px-4 py-3">Alert Type</th>
                      <th className="px-4 py-3">Device Name</th>
                      <th className="px-4 py-3">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.criticalAlerts.slice(0, 10).map((a, i) => (
                      <tr key={i} className="border-b border-border/50 hover:bg-surface/50">
                        <td className="px-4 py-3 text-error font-medium">{a.alert_type}</td>
                        <td className="px-4 py-3 text-textMuted">{a.device_name}</td>
                        <td className="px-4 py-3"><Badge status={a.status} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-bold text-textMain mb-4 flex items-center gap-2">
                <span className="text-primary">&gt;</span> view_open_incidents ({data.openIncidents.length})
              </h3>
              <div className="overflow-x-auto bg-background rounded-lg border border-border">
                <table className="w-full text-sm text-left">
                  <thead className="bg-surface text-textMuted font-mono text-xs uppercase">
                    <tr>
                      <th className="px-4 py-3">Title</th>
                      <th className="px-4 py-3">Severity</th>
                      <th className="px-4 py-3">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.openIncidents.slice(0, 10).map((inc, i) => (
                      <tr key={i} className="border-b border-border/50 hover:bg-surface/50">
                        <td className="px-4 py-3 text-textMain font-medium">{inc.title}</td>
                        <td className="px-4 py-3"><Badge status={inc.severity} /></td>
                        <td className="px-4 py-3"><Badge status={inc.status} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'triggers' && (
          <div>
            <h3 className="text-lg font-bold text-textMain mb-4 flex items-center gap-2">
              <span className="text-primary">&gt;</span> trg_device_status_change Log ({data.triggerHistory.length})
            </h3>
            <p className="text-textMuted text-sm mb-4">
              This log is automatically populated by an SQLite Trigger whenever a device's status changes.
            </p>
            <div className="overflow-x-auto bg-background rounded-lg border border-border">
              <table className="w-full text-sm text-left">
                <thead className="bg-surface text-textMuted font-mono text-xs uppercase">
                  <tr>
                    <th className="px-4 py-3">Device ID</th>
                    <th className="px-4 py-3">Prev Status</th>
                    <th className="px-4 py-3">New Status</th>
                    <th className="px-4 py-3">Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {data.triggerHistory.length === 0 ? (
                    <tr><td colSpan="4" className="px-4 py-4 text-center text-textMuted">No trigger events recorded yet. Edit a device status to see this in action.</td></tr>
                  ) : (
                    data.triggerHistory.map((log, i) => (
                      <tr key={i} className="border-b border-border/50 hover:bg-surface/50">
                        <td className="px-4 py-3 text-textMain font-mono">#{log.device_id}</td>
                        <td className="px-4 py-3"><Badge status={log.previous_status} /></td>
                        <td className="px-4 py-3"><Badge status={log.new_status} /></td>
                        <td className="px-4 py-3 text-textMuted">{new Date(log.changed_at).toLocaleString()}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'procedures' && (
          <div>
            <h3 className="text-lg font-bold text-textMain mb-4 flex items-center gap-2">
              <span className="text-primary">&gt;</span> SP_NETWORK_STATS (Mock Procedure Output)
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-background border border-border rounded-xl">
                <p className="text-textMuted text-xs uppercase tracking-widest mb-1">Total Devices</p>
                <p className="text-2xl font-bold text-primary font-mono">{data.procedureStats.total_devices}</p>
              </div>
              <div className="p-4 bg-background border border-border rounded-xl">
                <p className="text-textMuted text-xs uppercase tracking-widest mb-1">Online</p>
                <p className="text-2xl font-bold text-success font-mono">{data.procedureStats.online_devices}</p>
              </div>
              <div className="p-4 bg-background border border-border rounded-xl">
                <p className="text-textMuted text-xs uppercase tracking-widest mb-1">Avg CPU</p>
                <p className="text-2xl font-bold text-warning font-mono">{Number(data.procedureStats.avg_cpu).toFixed(1)}%</p>
              </div>
              <div className="p-4 bg-background border border-border rounded-xl">
                <p className="text-textMuted text-xs uppercase tracking-widest mb-1">Avg Memory</p>
                <p className="text-2xl font-bold text-info font-mono">{Number(data.procedureStats.avg_memory).toFixed(1)}%</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'indexes' && (
          <div>
            <h3 className="text-lg font-bold text-textMain mb-4 flex items-center gap-2">
              <span className="text-primary">&gt;</span> Database Indexes ({data.indexes.length})
            </h3>
            <div className="overflow-x-auto bg-background rounded-lg border border-border">
              <table className="w-full text-sm text-left">
                <thead className="bg-surface text-textMuted font-mono text-xs uppercase">
                  <tr>
                    <th className="px-4 py-3">Index Name</th>
                    <th className="px-4 py-3">Target Table</th>
                  </tr>
                </thead>
                <tbody>
                  {data.indexes.map((idx, i) => (
                    <tr key={i} className="border-b border-border/50 hover:bg-surface/50">
                      <td className="px-4 py-3 text-primary font-mono font-bold">{idx.index_name}</td>
                      <td className="px-4 py-3 text-textMain">{idx.table_name}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
