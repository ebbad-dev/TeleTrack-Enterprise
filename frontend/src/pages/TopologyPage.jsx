import React, { useEffect, useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { devicesApi, networkApi } from '../api';
import { extractItems } from '../api/helpers';
import { NetworkMap3D } from '../components/features/NetworkMap3D';
import { Badge } from '../components/ui/Badge';

export function TopologyPage() {
  const [devices, setDevices] = useState([]);
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    const fetch = async () => {
      try {
        const [dRes, lRes] = await Promise.all([devicesApi.getDevices(), networkApi.getLinks()]);
        setDevices(extractItems(dRes));
        setLinks(extractItems(lRes));
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    };
    fetch();
  }, []);

  const filteredDevices = useMemo(() =>
    filterStatus === 'all' ? devices : devices.filter(d => d.status === filterStatus),
    [devices, filterStatus]
  );

  return (
    <motion.div className="h-full flex flex-col -m-4 sm:-m-6 md:-m-8" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      {/* Header */}
      <div className="p-4 sm:p-6 pb-3 shrink-0 flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-textMain tracking-tight">
            Infrastructure <span className="text-primary neon-text">Topology</span>
          </h1>
          <p className="text-textMuted mt-0.5 font-mono text-xs uppercase tracking-widest">
            {filteredDevices.length} nodes • {links.length} links
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* Status filters */}
          {['all', 'online', 'offline', 'degraded'].map(s => (
            <button key={s} onClick={() => setFilterStatus(s)}
              className={`px-3 py-1.5 rounded-lg text-[10px] font-mono uppercase tracking-wider border transition-all
                ${filterStatus === s ? 'bg-primary/10 border-primary/40 text-primary' : 'bg-surface border-border text-textMuted hover:border-primary/20'}`}>
              {s === 'all' ? `All (${devices.length})` : `${s} (${devices.filter(d => d.status === s).length})`}
            </button>
          ))}
        </div>
      </div>

      {/* Canvas */}
      <div className="flex-1 relative bg-background border-t border-border">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center z-10">
            <div className="text-center space-y-3">
              <div className="w-12 h-12 border-3 border-primary/30 border-t-primary rounded-full animate-spin mx-auto" />
              <p className="text-primary font-mono text-sm animate-pulse">SCANNING NETWORK...</p>
            </div>
          </div>
        ) : (
          <NetworkMap3D devices={filteredDevices} links={links} />
        )}
      </div>
    </motion.div>
  );
}
