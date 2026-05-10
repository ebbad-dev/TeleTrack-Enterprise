import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Wrench } from 'lucide-react';
import { maintenanceApi } from '../api';
import { DataTable } from '../components/ui/DataTable';
import { format } from 'date-fns';

export function MaintenancePage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [globalFilter, setGlobalFilter] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await maintenanceApi.getMaintenance();
        if (res.success && res.data) setData(res.data);
      } catch (error) {
        console.error('Failed to fetch maintenance logs', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const columns = [
    {
      accessorKey: 'scheduled_date',
      header: 'Scheduled',
      cell: (info) => {
        const date = new Date(info.getValue());
        return (
          <div className="font-mono text-xs text-textMuted">
            <span className="text-primary">{format(date, 'yyyy-MM-dd')}</span>
          </div>
        );
      },
    },
    {
      accessorKey: 'device',
      header: 'Target Hardware',
      cell: (info) => {
        const device = info.getValue() || { device_name: `NODE-${info.row.original.device_id}` };
        return (
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded bg-surfaceHighlight border border-border flex items-center justify-center">
              <Wrench size={14} className="text-primary/70" />
            </div>
            <span className="font-bold text-textMain">{device.device_name}</span>
          </div>
        );
      },
    },
    {
      accessorKey: 'maintenance_type',
      header: 'Op Type',
      cell: (info) => <span className="text-xs uppercase tracking-wider font-semibold text-textMain">{info.getValue()}</span>,
    },
    {
      accessorKey: 'technician',
      header: 'Assigned Tech',
      cell: (info) => {
        const tech = info.getValue();
        return <span className="text-sm">{tech ? tech.full_name : 'Unassigned'}</span>;
      },
    },
    {
      accessorKey: 'outcome',
      header: 'Outcome',
      cell: (info) => {
        const outcome = info.getValue();
        return (
          <span className={`font-mono text-xs uppercase tracking-widest ${outcome === 'Successful' ? 'text-success' : outcome === 'Failed' ? 'text-error' : 'text-warning'}`}>
            {outcome || 'PENDING'}
          </span>
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
          <h1 className="text-3xl font-bold text-textMain tracking-wide">SYSTEM <span className="text-primary neon-text">MAINTENANCE</span></h1>
          <p className="text-textMuted mt-1 font-mono text-sm uppercase">Preventive & Corrective Actions</p>
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
            placeholder="Search maintenance logs..."
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
        />
      </div>
    </motion.div>
  );
}
