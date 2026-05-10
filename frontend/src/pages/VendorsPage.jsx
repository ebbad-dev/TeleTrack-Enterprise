import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Globe, Mail, Phone } from 'lucide-react';
import { vendorsApi } from '../api';
import { DataTable } from '../components/ui/DataTable';

export function VendorsPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [globalFilter, setGlobalFilter] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await vendorsApi.getVendors();
        if (res.success && res.data) {
          const items = res.data.items || (Array.isArray(res.data) ? res.data : []);
          setData(items);
        }
      } catch (error) {
        console.error('Failed to fetch vendors', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const columns = [
    {
      accessorKey: 'vendor_name',
      header: 'Vendor Identity',
      cell: (info) => {
        const vendor = info.row.original;
        const avatarUrl = `https://api.dicebear.com/7.x/initials/svg?seed=${vendor.vendor_name}&backgroundColor=00f0ff&textColor=0a0a0f`;
        return (
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded bg-primary/20 border border-primary/50 p-0.5 overflow-hidden shadow-[0_0_10px_rgba(0,240,255,0.2)]">
              <img src={avatarUrl} alt="avatar" className="w-full h-full object-cover rounded-sm" />
            </div>
            <div>
              <p className="font-bold text-textMain group-hover:text-primary transition-colors">{vendor.vendor_name}</p>
              <p className="text-xs text-textMuted flex items-center mt-0.5"><Globe size={10} className="mr-1"/> {vendor.country_of_origin}</p>
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: 'support_email',
      header: 'Support Channel',
      cell: (info) => (
        <div className="flex items-center space-x-2 text-textMuted">
          <Mail size={14} className="text-primary/70" />
          <span className="font-mono text-xs">{info.getValue()}</span>
        </div>
      ),
    },
    {
      accessorKey: 'support_phone',
      header: 'Direct Line',
      cell: (info) => (
        <div className="flex items-center space-x-2 text-textMuted">
          <Phone size={14} className="text-primary/70" />
          <span className="font-mono text-xs">{info.getValue() || 'N/A'}</span>
        </div>
      ),
    },
    {
      accessorKey: 'website',
      header: 'Extranet',
      cell: (info) => (
        <a href={info.getValue()} target="_blank" rel="noreferrer" className="text-primary hover:underline font-mono text-xs truncate max-w-[150px] inline-block">
          {info.getValue()}
        </a>
      ),
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
          <h1 className="text-3xl font-bold text-textMain tracking-wide">SUPPLY <span className="text-primary neon-text">CHAIN</span></h1>
          <p className="text-textMuted mt-1 font-mono text-sm uppercase">Vendor & Partner Directory</p>
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
            placeholder="Search partners..."
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
