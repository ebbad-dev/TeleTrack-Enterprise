import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { databaseApi } from '../api';
import { Database, Eye, Zap, Search, Settings, ChevronRight, Play, ArrowUpDown } from 'lucide-react';
import { Badge } from '../components/ui/Badge';

function StatusBadge({ status }) {
  if (!status) return null;
  const s = String(status).toLowerCase();
  let variant = 'default';
  if (['online', 'success', 'resolved', 'active'].includes(s)) variant = 'success';
  else if (['offline', 'error', 'failed', 'critical', 'high'].includes(s)) variant = 'error';
  else if (['degraded', 'warning', 'medium', 'open'].includes(s)) variant = 'warning';
  else if (['info', 'low', 'closed'].includes(s)) variant = 'info';
  
  return <Badge variant={variant}>{status.toUpperCase()}</Badge>;
}

export function DatabaseStatsPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({
    activeDevices: [],
    criticalAlerts: [],
    openIncidents: [],
    triggerHistory: [],
    indexes: []
  });
  
  const [activeTab, setActiveTab] = useState('views');

  // Sorting state for views
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  // Procedure state
  const [procedureStats, setProcedureStats] = useState(null);
  const [procLoading, setProcLoading] = useState(false);

  // Indexes state
  const [indexSample, setIndexSample] = useState(null);
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [indexLoading, setIndexLoading] = useState(false);
  const [indexError, setIndexError] = useState(null);

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      try {
        const [
          activeDevices,
          criticalAlerts,
          openIncidents,
          triggerHistory,
          indexes
        ] = await Promise.all([
          databaseApi.getActiveDevicesView(),
          databaseApi.getCriticalAlertsView(),
          databaseApi.getOpenIncidentsView(),
          databaseApi.getTriggerHistory(),
          databaseApi.getIndexes()
        ]);
        
        setData({
          activeDevices: activeDevices.data || [],
          criticalAlerts: criticalAlerts.data || [],
          openIncidents: openIncidents.data || [],
          triggerHistory: triggerHistory.data || [],
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

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const getSortedData = (list) => {
    if (!sortConfig.key) return list;
    return [...list].sort((a, b) => {
      if (a[sortConfig.key] < b[sortConfig.key]) return sortConfig.direction === 'asc' ? -1 : 1;
      if (a[sortConfig.key] > b[sortConfig.key]) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  };

  const executeProcedure = async () => {
    setProcLoading(true);
    try {
      const res = await databaseApi.getProcedureStats();
      setTimeout(() => {
        setProcedureStats(res.data);
        setProcLoading(false);
      }, 600); // Artificial delay to simulate processing
    } catch (e) {
      console.error(e);
      setProcLoading(false);
    }
  };

  const loadIndexSample = async (idx) => {
    setSelectedIndex(idx);
    setIndexSample(null);
    setIndexError(null);
    if (!idx.column_name) {
        setIndexError("Index has no extractable column name.");
        return;
    }
    setIndexLoading(true);
    try {
      const res = await databaseApi.getIndexSample(idx.table_name, idx.column_name);
      setIndexSample(res.data);
    } catch (e) {
      console.error(e);
      setIndexError(e.response?.data?.error || e.message || "Failed to load index sample");
    } finally {
      setIndexLoading(false);
    }
  };

  const tabs = [
    { id: 'views', label: 'SQL Views', icon: Eye },
    { id: 'triggers', label: 'Triggers (History)', icon: Zap },
    { id: 'procedures', label: 'Procedures (Complex Query)', icon: Settings },
    { id: 'indexes', label: 'Indexes', icon: Search },
    { id: 'timetravel', label: 'Time Travel (CTE)', icon: Database }
  ];

  // Predictive Analytics
  const [predictiveStats, setPredictiveStats] = useState(null);
  const [predLoading, setPredLoading] = useState(false);

  // Time Travel
  const [timeTarget, setTimeTarget] = useState(new Date().toISOString().slice(0, 16));
  const [timeSnapshot, setTimeSnapshot] = useState(null);
  const [timeLoading, setTimeLoading] = useState(false);

  const executePredictive = async () => {
    setPredLoading(true);
    try {
      const res = await databaseApi.getPredictiveAnalytics();
      setTimeout(() => {
        setPredictiveStats(res.data);
        setPredLoading(false);
      }, 800);
    } catch (e) {
      console.error(e);
      setPredLoading(false);
    }
  };

  const executeTimeTravel = async () => {
    setTimeLoading(true);
    try {
      // Need seconds for ISO 8601 that the backend parses
      const formatted = timeTarget.length === 16 ? timeTarget + ':00' : timeTarget;
      const res = await databaseApi.getTimeTravel(formatted);
      setTimeout(() => {
        setTimeSnapshot(res.data);
        setTimeLoading(false);
      }, 500);
    } catch (e) {
      console.error(e);
      setTimeLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="w-12 h-12 border-3 border-primary/30 border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  const SortableHeader = ({ label, sortKey }) => (
    <th className="px-4 py-3 cursor-pointer hover:bg-surfaceHighlight transition-colors" onClick={() => handleSort(sortKey)}>
      <div className="flex items-center gap-1.5">
        {label}
        <ArrowUpDown size={12} className={sortConfig.key === sortKey ? "text-primary" : "text-textMuted/50"} />
      </div>
    </th>
  );

  return (
    <motion.div className="h-full flex flex-col -m-4 sm:-m-6 md:-m-8" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="p-4 sm:p-6 pb-4 shrink-0 border-b border-border bg-surface/50 backdrop-blur">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-primary/10 rounded-xl border border-primary/30">
            <Database size={24} className="text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-textMain tracking-tight">
              Database <span className="text-primary neon-text">Explorer</span>
            </h1>
            <p className="text-textMuted text-xs uppercase tracking-widest font-mono mt-1">
              Test & Interact with Database Objects
            </p>
          </div>
        </div>
        <div className="flex gap-2 mt-6 overflow-x-auto custom-scrollbar pb-2">
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
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-4 sm:p-6 space-y-6">
        
        {activeTab === 'views' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
            <div className="glass-panel p-5">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-textMain flex items-center gap-2">
                  <span className="text-primary">&gt;</span> view_active_devices ({data.activeDevices.length})
                </h3>
                <span className="text-xs font-mono text-textMuted">Click headers to sort</span>
              </div>
              <div className="overflow-x-auto bg-background rounded-lg border border-border custom-scrollbar max-h-64">
                <table className="w-full text-sm text-left">
                  <thead className="bg-surface text-textMuted font-mono text-xs uppercase sticky top-0 z-10">
                    <tr>
                      <SortableHeader label="Device Name" sortKey="device_name" />
                      <SortableHeader label="Type" sortKey="device_type" />
                      <SortableHeader label="Status" sortKey="status" />
                    </tr>
                  </thead>
                  <tbody>
                    {getSortedData(data.activeDevices).map((d, i) => (
                      <tr key={i} className="border-b border-border/50 hover:bg-surface/50">
                        <td className="px-4 py-3 text-textMain font-medium">{d.device_name}</td>
                        <td className="px-4 py-3 text-textMuted">{d.device_type}</td>
                        <td className="px-4 py-3"><StatusBadge status={d.status} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="glass-panel p-5">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-textMain flex items-center gap-2">
                  <span className="text-primary">&gt;</span> view_critical_alerts ({data.criticalAlerts.length})
                </h3>
                <span className="text-xs font-mono text-textMuted">Click headers to sort</span>
              </div>
              <div className="overflow-x-auto bg-background rounded-lg border border-border custom-scrollbar max-h-64">
                <table className="w-full text-sm text-left">
                  <thead className="bg-surface text-textMuted font-mono text-xs uppercase sticky top-0 z-10">
                    <tr>
                      <SortableHeader label="Alert Type" sortKey="alert_type" />
                      <SortableHeader label="Device Name" sortKey="device_name" />
                      <SortableHeader label="Status" sortKey="status" />
                    </tr>
                  </thead>
                  <tbody>
                    {getSortedData(data.criticalAlerts).map((a, i) => (
                      <tr key={i} className="border-b border-border/50 hover:bg-surface/50">
                        <td className="px-4 py-3 text-error font-medium">{a.alert_type}</td>
                        <td className="px-4 py-3 text-textMuted">{a.device_name}</td>
                        <td className="px-4 py-3"><StatusBadge status={a.status} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            
            <div className="glass-panel p-5">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-textMain flex items-center gap-2">
                  <span className="text-primary">&gt;</span> view_open_incidents ({data.openIncidents.length})
                </h3>
                <span className="text-xs font-mono text-textMuted">Click headers to sort</span>
              </div>
              <div className="overflow-x-auto bg-background rounded-lg border border-border custom-scrollbar max-h-64">
                <table className="w-full text-sm text-left">
                  <thead className="bg-surface text-textMuted font-mono text-xs uppercase sticky top-0 z-10">
                    <tr>
                      <SortableHeader label="Title" sortKey="title" />
                      <SortableHeader label="Severity" sortKey="severity" />
                      <SortableHeader label="Status" sortKey="status" />
                    </tr>
                  </thead>
                  <tbody>
                    {getSortedData(data.openIncidents).map((inc, i) => (
                      <tr key={i} className="border-b border-border/50 hover:bg-surface/50">
                        <td className="px-4 py-3 text-textMain font-medium">{inc.title}</td>
                        <td className="px-4 py-3"><StatusBadge status={inc.severity} /></td>
                        <td className="px-4 py-3"><StatusBadge status={inc.status} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'triggers' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-panel p-6">
            <h3 className="text-lg font-bold text-textMain mb-4 flex items-center gap-2">
              <span className="text-primary">&gt;</span> trg_device_status_change Log ({data.triggerHistory.length})
            </h3>
            <p className="text-textMuted text-sm mb-4">
              This log is automatically populated by an SQLite Trigger whenever a device's status changes.
            </p>
            <div className="overflow-x-auto bg-background rounded-lg border border-border custom-scrollbar max-h-96">
              <table className="w-full text-sm text-left">
                <thead className="bg-surface text-textMuted font-mono text-xs uppercase sticky top-0 z-10">
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
                        <td className="px-4 py-3"><StatusBadge status={log.previous_status} /></td>
                        <td className="px-4 py-3"><StatusBadge status={log.new_status} /></td>
                        <td className="px-4 py-3 text-textMuted">{new Date(log.changed_at).toLocaleString()}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}

        {activeTab === 'procedures' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-panel p-6 max-w-4xl mx-auto text-center mt-12">
            <div className="mb-8">
              <Settings size={48} className="mx-auto text-primary/50 mb-4" />
              <h3 className="text-2xl font-bold text-textMain mb-2">SP_NETWORK_STATS</h3>
              <p className="text-textMuted">Executes a complex server-side query to aggregate total infrastructure metrics.</p>
            </div>
            
            {!procedureStats && (
              <button onClick={executeProcedure} disabled={procLoading}
                className="mx-auto flex items-center gap-2 px-6 py-3 bg-primary text-background font-bold uppercase tracking-wider rounded-lg hover:brightness-110 disabled:opacity-50 btn-ripple shadow-[0_0_20px_rgba(0,240,255,0.3)]">
                {procLoading ? <div className="w-5 h-5 border-2 border-background border-t-transparent rounded-full animate-spin" /> : <Play size={18} />}
                Execute Procedure
              </button>
            )}

            <AnimatePresence>
              {procedureStats && (
                <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="mt-8">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-4 bg-background border border-border rounded-xl">
                      <p className="text-textMuted text-xs uppercase tracking-widest mb-1">Total Devices</p>
                      <p className="text-2xl font-bold text-primary font-mono">{procedureStats.total_devices}</p>
                    </div>
                    <div className="p-4 bg-background border border-border rounded-xl">
                      <p className="text-textMuted text-xs uppercase tracking-widest mb-1">Online</p>
                      <p className="text-2xl font-bold text-success font-mono">{procedureStats.online_devices}</p>
                    </div>
                    <div className="p-4 bg-background border border-border rounded-xl">
                      <p className="text-textMuted text-xs uppercase tracking-widest mb-1">Avg CPU</p>
                      <p className="text-2xl font-bold text-warning font-mono">{Number(procedureStats.avg_cpu).toFixed(1)}%</p>
                    </div>
                    <div className="p-4 bg-background border border-border rounded-xl">
                      <p className="text-textMuted text-xs uppercase tracking-widest mb-1">Avg Memory</p>
                      <p className="text-2xl font-bold text-info font-mono">{Number(procedureStats.avg_memory).toFixed(1)}%</p>
                    </div>
                  </div>
                  <button onClick={() => setProcedureStats(null)} className="mt-6 text-sm text-primary hover:underline font-mono">
                    Reset Procedure
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="mt-16 mb-8 border-t border-border pt-8">
              <Zap size={48} className="mx-auto text-warning/50 mb-4" />
              <h3 className="text-2xl font-bold text-textMain mb-2">SP_PREDICTIVE_MAINTENANCE</h3>
              <p className="text-textMuted">Advanced query analyzing historical alerts to calculate failure probability.</p>
            </div>
            
            {!predictiveStats && (
              <button onClick={executePredictive} disabled={predLoading}
                className="mx-auto flex items-center gap-2 px-6 py-3 bg-warning/20 text-warning font-bold uppercase tracking-wider rounded-lg hover:bg-warning/30 disabled:opacity-50 border border-warning/50 shadow-[0_0_20px_rgba(255,179,0,0.1)]">
                {predLoading ? <div className="w-5 h-5 border-2 border-warning border-t-transparent rounded-full animate-spin" /> : <Play size={18} />}
                Run Predictive AI
              </button>
            )}

            <AnimatePresence>
              {predictiveStats && (
                <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="mt-8">
                  <div className="overflow-x-auto bg-background rounded-lg border border-border custom-scrollbar max-h-64 text-left">
                    <table className="w-full text-sm text-left">
                      <thead className="bg-surface text-textMuted font-mono text-xs uppercase sticky top-0 z-10">
                        <tr>
                          <th className="px-4 py-3">Device Name</th>
                          <th className="px-4 py-3">Type</th>
                          <th className="px-4 py-3">Recent Alerts</th>
                          <th className="px-4 py-3">Failure Prob.</th>
                        </tr>
                      </thead>
                      <tbody>
                        {predictiveStats.map((d, i) => (
                          <tr key={i} className="border-b border-border/50 hover:bg-surface/50">
                            <td className="px-4 py-3 text-textMain font-medium">{d.device_name}</td>
                            <td className="px-4 py-3 text-textMuted">{d.device_type}</td>
                            <td className="px-4 py-3 text-warning font-mono">{d.recent_alerts}</td>
                            <td className="px-4 py-3 font-bold">
                              <span className={d.failure_probability > 50 ? 'text-error' : 'text-warning'}>
                                {d.failure_probability}%
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <button onClick={() => setPredictiveStats(null)} className="mt-6 text-sm text-warning hover:underline font-mono">
                    Reset Prediction
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

          </motion.div>
        )}

        {activeTab === 'timetravel' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-panel p-6">
            <h3 className="text-xl font-bold text-textMain mb-2 flex items-center gap-2">
              <span className="text-primary">&gt;</span> Chronological State Reconstructor (CTE)
            </h3>
            <p className="text-textMuted text-sm mb-6">
              Uses Common Table Expressions (CTEs) and Window Functions to query the historical audit logs and recreate the exact network state at a specific past timestamp.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 items-end mb-8 bg-background p-4 rounded-xl border border-border">
              <div className="flex-1 w-full">
                <label className="block text-xs font-mono uppercase text-textMuted mb-2">Target Timestamp</label>
                <input 
                  type="datetime-local" 
                  value={timeTarget} 
                  onChange={(e) => setTimeTarget(e.target.value)}
                  className="w-full bg-surface border border-border rounded-lg px-4 py-2 text-textMain focus:outline-none focus:border-primary"
                />
              </div>
              <button 
                onClick={executeTimeTravel} 
                disabled={timeLoading}
                className="w-full sm:w-auto px-6 py-2 bg-primary/20 text-primary font-bold tracking-widest uppercase border border-primary/50 rounded-lg hover:bg-primary/30 flex items-center justify-center gap-2"
              >
                {timeLoading ? <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" /> : "Initiate Jump"}
              </button>
            </div>

            <AnimatePresence>
              {timeSnapshot && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
                  <div className="flex justify-between items-center mb-4">
                    <h4 className="font-bold text-success font-mono uppercase">Snapshot Reconstructed</h4>
                    <span className="text-xs text-textMuted font-mono">Total Nodes: {timeSnapshot.length}</span>
                  </div>
                  
                  <div className="overflow-x-auto bg-background rounded-lg border border-border custom-scrollbar max-h-96 text-left">
                    <table className="w-full text-sm text-left">
                      <thead className="bg-surface text-textMuted font-mono text-xs uppercase sticky top-0 z-10">
                        <tr>
                          <th className="px-4 py-3">ID</th>
                          <th className="px-4 py-3">Device Name</th>
                          <th className="px-4 py-3">Status at T0</th>
                          <th className="px-4 py-3">Current Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {timeSnapshot.map((d, i) => (
                          <tr key={i} className="border-b border-border/50 hover:bg-surface/50">
                            <td className="px-4 py-3 font-mono text-textMuted">#{d.device_id}</td>
                            <td className="px-4 py-3 text-textMain">{d.device_name}</td>
                            <td className="px-4 py-3">
                              <StatusBadge status={d.historical_status} />
                              {d.historical_status !== d.current_status && (
                                <span className="ml-2 text-[10px] text-warning uppercase font-mono border border-warning/30 rounded px-1">Changed</span>
                              )}
                            </td>
                            <td className="px-4 py-3 opacity-50"><StatusBadge status={d.current_status} /></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {activeTab === 'indexes' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col lg:flex-row gap-6">
            {/* Left side: Indexes List */}
            <div className="glass-panel p-6 lg:w-1/3 shrink-0 self-start">
              <h3 className="text-lg font-bold text-textMain mb-4 flex items-center gap-2">
                <span className="text-primary">&gt;</span> Database Indexes
              </h3>
              <p className="text-sm text-textMuted mb-4">Click an index to execute an optimized sort query.</p>
              
              <div className="space-y-2">
                {data.indexes.map((idx, i) => (
                  <button key={i} onClick={() => loadIndexSample(idx)}
                    disabled={!idx.column_name}
                    className={`w-full flex items-center justify-between p-3 rounded-lg border text-left transition-all group
                      ${selectedIndex?.index_name === idx.index_name ? 'bg-primary/10 border-primary text-textMain shadow-[0_0_10px_rgba(0,240,255,0.2)]' : 'bg-background border-border text-textMuted hover:border-primary/50'}`}>
                    <div>
                      <p className="font-mono font-bold text-primary group-hover:text-primary transition-colors">{idx.index_name}</p>
                      <p className="text-xs uppercase tracking-wider mt-1 opacity-70">Table: {idx.table_name}</p>
                    </div>
                    <ChevronRight size={16} className={`opacity-0 group-hover:opacity-100 transition-opacity ${selectedIndex?.index_name === idx.index_name ? 'opacity-100 text-primary' : ''}`} />
                  </button>
                ))}
              </div>
            </div>
            
            {/* Right side: Index Result Viewer */}
            <div className="glass-panel p-6 flex-1 min-h-[400px] flex flex-col">
              {selectedIndex ? (
                <>
                  <div className="mb-4">
                    <h3 className="text-lg font-bold text-textMain flex items-center gap-2">
                      Executing via Index: <span className="text-primary">{selectedIndex.index_name}</span>
                    </h3>
                    <p className="text-xs text-textMuted font-mono mt-1">
                      Query: <span className="text-success">SELECT * FROM {selectedIndex.table_name} ORDER BY {selectedIndex.column_name}</span>
                    </p>
                  </div>
                  
                  {indexLoading ? (
                    <div className="flex-1 flex items-center justify-center">
                      <div className="w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
                    </div>
                  ) : indexError ? (
                    <div className="p-4 bg-error/10 border border-error/30 text-error rounded-lg">
                      {indexError}
                    </div>
                  ) : indexSample ? (
                    <div className="overflow-x-auto bg-background rounded-lg border border-border custom-scrollbar flex-1 max-h-[500px]">
                      <table className="w-full text-sm text-left">
                        <thead className="bg-surface text-textMuted font-mono text-xs uppercase sticky top-0 z-10">
                          <tr>
                            {Object.keys(indexSample[0] || {}).slice(0, 5).map(k => (
                              <th key={k} className={`px-4 py-3 ${k === selectedIndex.column_name ? 'text-primary bg-primary/5' : ''}`}>
                                {k} {k === selectedIndex.column_name && '(Indexed)'}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {indexSample.map((row, i) => (
                            <tr key={i} className="border-b border-border/50 hover:bg-surface/50">
                              {Object.entries(row).slice(0, 5).map(([k, val], j) => (
                                <td key={j} className={`px-4 py-3 ${k === selectedIndex.column_name ? 'font-bold text-textMain bg-primary/5' : 'text-textMuted'}`}>
                                  {typeof val === 'string' && (val === 'critical' || val === 'online' || val === 'offline' || val === 'open') ? <StatusBadge status={val} /> : String(val)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {indexSample.length === 0 && <p className="p-4 text-center text-textMuted">No data in table.</p>}
                    </div>
                  ) : null}
                </>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-textMuted/50">
                  <Search size={48} className="mb-4 opacity-50" />
                  <p>Select an index from the left panel to execute</p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
