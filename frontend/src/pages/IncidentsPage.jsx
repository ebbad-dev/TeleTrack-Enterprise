import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Flame } from 'lucide-react';
import { incidentsApi, exportApi } from '../api';
import { DataTable } from '../components/ui/DataTable';
import { Badge } from '../components/ui/Badge';
import { format } from 'date-fns';

export function IncidentsPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [globalFilter, setGlobalFilter] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await incidentsApi.getIncidents();
        if (res.success && res.data) setData(res.data);
      } catch (error) {
        console.error('Failed to fetch incidents', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const columns = [
    {
      accessorKey: 'reported_at',
      header: 'Reported T-Zero',
      cell: (info) => {
        const date = new Date(info.getValue());
        return (
          <div className="font-mono text-xs text-textMuted">
            <span className="text-primary">{format(date, 'yyyy-MM-dd')}</span>
            <br />
            {format(date, 'HH:mm:ss')}
          </div>
        );
      },
    },
    {
      accessorKey: 'title',
      header: 'Incident Designation',
      cell: (info) => {
        const inc = info.row.original;
        return (
          <div className="flex items-center space-x-3">
            <div className={`w-8 h-8 rounded bg-surfaceHighlight border flex items-center justify-center ${inc.severity === 'critical' ? 'border-error text-error' : 'border-warning text-warning'}`}>
              <Flame size={16} />
            </div>
            <div>
              <p className="font-bold text-textMain">{inc.title}</p>
              <p className="text-xs text-textMuted max-w-[250px] truncate">{inc.description}</p>
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: 'severity',
      header: 'Severity',
      cell: (info) => {
        const severity = info.getValue();
        return (
          <Badge variant={
            severity === 'critical' ? 'error' : 
            severity === 'high' ? 'warning' : 
            severity === 'medium' ? 'info' : 'default'
          }>
            {severity.toUpperCase()}
          </Badge>
        );
      },
    },
    {
      accessorKey: 'status',
      header: 'Resolution Status',
      cell: (info) => {
        const status = info.getValue();
        return (
          <span className={`font-mono text-xs uppercase tracking-widest ${status === 'resolved' ? 'text-success' : status === 'open' ? 'text-error' : 'text-primary'}`}>
            {status.replace('_', ' ')}
          </span>
        );
      },
    },
    {
      accessorKey: 'impact',
      header: 'Blast Radius',
      cell: (info) => <span className="text-textMuted text-xs">{info.getValue() || 'Unknown'}</span>,
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
          <h1 className="text-3xl font-bold text-textMain tracking-wide">INCIDENT <span className="text-error neon-text">RESPONSE</span></h1>
          <p className="text-textMuted mt-1 font-mono text-sm uppercase">Major Outages & Investigations</p>
        </div>
        
        <div className="relative w-full md:w-72">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-error">
            <Search size={18} />
          </div>
          <input
            type="text"
            value={globalFilter ?? ''}
            onChange={e => setGlobalFilter(e.target.value)}
            className="w-full bg-surface/50 backdrop-blur-md border border-error/30 rounded-lg py-2 pl-10 pr-4 text-textMain focus:outline-none focus:border-error focus:ring-1 focus:ring-error shadow-[0_0_15px_rgba(255,0,60,0.1)] transition-all placeholder-textMuted/50 font-mono text-sm"
            placeholder="Search incident logs..."
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
          onExport={() => exportApi.exportIncidents()}
          exportLabel="Export CSV"
        />
      </div>
    </motion.div>
  );
}
