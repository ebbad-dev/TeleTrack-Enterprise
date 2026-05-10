import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Search, ShieldCheck } from 'lucide-react';
import { auditApi, exportApi } from '../api';
import { DataTable } from '../components/ui/DataTable';
import { format } from 'date-fns';

export function AuditLogPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [globalFilter, setGlobalFilter] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await auditApi.getLogs();
        if (res.success && res.data) setData(res.data);
      } catch (error) {
        console.error('Failed to fetch audit logs', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const columns = [
    {
      accessorKey: 'timestamp',
      header: 'Event Time',
      cell: (info) => {
        const date = new Date(info.getValue());
        return (
          <div className="font-mono text-xs text-textMuted">
            <span className="text-primary">{format(date, 'yyyy-MM-dd')}</span>
            <br />
            {format(date, 'HH:mm:ss.SSS')}
          </div>
        );
      },
    },
    {
      accessorKey: 'user',
      header: 'Identity',
      cell: (info) => {
        const user = info.getValue();
        return (
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 rounded bg-primary/20 border border-primary/50 flex items-center justify-center">
              <ShieldCheck size={12} className="text-primary" />
            </div>
            <span className="font-bold text-textMain text-xs">{user ? user.username : 'SYSTEM'}</span>
          </div>
        );
      },
    },
    {
      accessorKey: 'action',
      header: 'Action',
      cell: (info) => <span className="font-mono text-xs uppercase tracking-widest text-primary/80">{info.getValue()}</span>,
    },
    {
      accessorKey: 'resource',
      header: 'Target Resource',
      cell: (info) => <span className="text-xs text-textMuted">{info.getValue()}</span>,
    },
    {
      accessorKey: 'ip_address',
      header: 'Source IP',
      cell: (info) => <span className="font-mono text-xs text-textMuted">{info.getValue()}</span>,
    },
  ];

  return (
    <motion.div 
      className="space-y-6 h-full flex flex-col"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 shrink-0">
        <div>
          <h1 className="text-3xl font-bold text-textMain tracking-wide">SECURITY <span className="text-primary neon-text">AUDIT</span></h1>
          <p className="text-textMuted mt-1 font-mono text-sm uppercase">Immutable Action Trail</p>
        </div>
        
        <div className="relative w-full md:w-72">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-primary">
            <Search size={18} />
          </div>
          <input
            type="text"
            value={globalFilter ?? ''}
            onChange={e => setGlobalFilter(e.target.value)}
            className="w-full bg-surface/50 backdrop-blur-md border border-primary/30 rounded-lg py-2 pl-10 pr-4 text-textMain focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary shadow-[0_0_15px_rgba(0,240,255,0.1)] transition-all placeholder-textMuted/50 font-mono text-sm"
            placeholder="Scan security events..."
          />
        </div>
      </div>

      <div className="flex-1 min-h-0">
        <DataTable 
          columns={columns} 
          data={data} 
          loading={loading} 
          globalFilter={globalFilter} 
          setGlobalFilter={setGlobalFilter} 
          onExport={(format) => exportApi.exportAuditLogs(format)}
        />
      </div>
    </motion.div>
  );
}
