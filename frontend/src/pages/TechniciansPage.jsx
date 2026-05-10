import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Search } from 'lucide-react';
import { techniciansApi } from '../api';
import { DataTable } from '../components/ui/DataTable';
import { Badge } from '../components/ui/Badge';

export function TechniciansPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [globalFilter, setGlobalFilter] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await techniciansApi.getTechnicians();
        if (res.success && res.data) setData(res.data);
      } catch (error) {
        console.error('Failed to fetch technicians', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const columns = [
    {
      accessorKey: 'full_name',
      header: 'Technician',
      cell: (info) => {
        const tech = info.row.original;
        const avatarUrl = `https://api.dicebear.com/7.x/adventurer/svg?seed=${tech.full_name}&backgroundColor=0a0a0f`;
        return (
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-surfaceHighlight border border-border p-0.5 overflow-hidden shadow-md">
              <img src={avatarUrl} alt="avatar" className="w-full h-full object-cover rounded-full" />
            </div>
            <div>
              <p className="font-bold text-textMain group-hover:text-primary transition-colors">{tech.full_name}</p>
              <p className="text-xs text-textMuted font-mono">{tech.email}</p>
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: 'specialization',
      header: 'Specialization',
    },
    {
      accessorKey: 'shift',
      header: 'Shift',
      cell: (info) => <span className="font-mono text-xs uppercase text-primary/80">{info.getValue()}</span>,
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: (info) => {
        const status = info.getValue();
        return (
          <Badge variant={status === 'available' ? 'success' : status === 'busy' ? 'warning' : 'default'}>
            {status.toUpperCase()}
          </Badge>
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
          <h1 className="text-3xl font-bold text-textMain tracking-wide">FIELD <span className="text-primary neon-text">OPERATIVES</span></h1>
          <p className="text-textMuted mt-1 font-mono text-sm uppercase">Technician Roster</p>
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
            placeholder="Search operatives..."
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
