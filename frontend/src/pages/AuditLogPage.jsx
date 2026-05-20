import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Search, History, Download, TerminalSquare } from 'lucide-react';
import { exportApi } from '../api';
import { auditApi } from '../api';
import { extractItems } from '../api/helpers';
import { DataTable } from '../components/ui/DataTable';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import useToastStore from '../store/toastStore';

export function AuditLogPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [globalFilter, setGlobalFilter] = useState('');
  const toast = useToastStore;

  const fetchData = async () => {
    try {
      const res = await auditApi.getLogs();
      setData(extractItems(res));
    } catch (error) {
      console.error('Failed to fetch audit logs', error);
      toast.error('Failed to load audit logs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const columns = [
    {
      accessorKey: 'timestamp',
      header: 'System Time',
      cell: (info) => (
        <div className="font-mono text-xs text-textMuted">
          <span className="text-primary">{new Date(info.getValue()).toLocaleDateString()}</span>
          <br />
          {new Date(info.getValue()).toLocaleTimeString()}
        </div>
      ),
    },
    {
      accessorKey: 'action',
      header: 'Execution Signature',
      cell: (info) => {
        const action = info.getValue();
        return (
          <div className="flex items-center space-x-2">
            <TerminalSquare size={14} className="text-primary/70" />
            <span className="font-mono text-sm font-bold tracking-widest text-textMain">{action}</span>
          </div>
        );
      },
    },
    {
      accessorKey: 'resource',
      header: 'Target Module',
      cell: (info) => <Badge variant="default">{info.getValue()?.toUpperCase()}</Badge>,
    },
    {
      accessorKey: 'user.username',
      header: 'Operator ID',
      cell: (info) => (
        <span className="font-mono text-xs text-textMuted flex items-center">
          {info.getValue() || `ID-${info.row.original.user_id}`}
        </span>
      ),
    },
    {
      accessorKey: 'details',
      header: 'Payload / Details',
      cell: (info) => {
        const details = info.getValue();
        return (
          <div className="max-w-[300px] truncate text-xs font-mono text-textMuted">
            {details ? JSON.stringify(details) : '—'}
          </div>
        );
      },
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
          <h1 className="text-3xl font-bold text-textMain tracking-wide">AUDIT <span className="text-warning neon-text">TRAIL</span></h1>
          <p className="text-textMuted mt-1 font-mono text-sm uppercase">Immutable Security Ledger</p>
        </div>
        
        <div className="flex items-center space-x-4 w-full md:w-auto">
          <div className="relative flex-1 md:w-72">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-warning">
              <Search size={18} />
            </div>
            <input
              type="text"
              value={globalFilter ?? ''}
              onChange={e => setGlobalFilter(e.target.value)}
              className="w-full bg-surface/50 backdrop-blur-md border border-warning/30 rounded-lg py-2 pl-10 pr-4 text-textMain focus:outline-none focus:border-warning focus:ring-1 focus:ring-warning shadow-[0_0_15px_rgba(255,179,0,0.1)] transition-all placeholder-textMuted/50 font-mono text-sm"
              placeholder="Query logs..."
            />
          </div>
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
