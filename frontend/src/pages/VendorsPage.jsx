import React, { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Search, Building2, Plus, Globe, Mail, Phone } from 'lucide-react';
import { vendorsApi } from '../api';
import { extractItems } from '../api/helpers';
import { DataTable } from '../components/ui/DataTable';
import { DataModal } from '../components/ui/DataModal';
import { Button } from '../components/ui/Button';
import useToastStore from '../store/toastStore';

export function VendorsPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [globalFilter, setGlobalFilter] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const toast = useToastStore;

  const fetchData = useCallback(async (showLoading = false) => {
    if (showLoading) setLoading(true);
    try {
      const res = await vendorsApi.getVendors();
      setData(extractItems(res));
    } catch (error) {
      console.error('Failed to fetch vendors', error);
      toast.error('Failed to load vendors');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData(true);
  }, [fetchData]);

  const handleDelete = async (id) => {
    if (!window.confirm("CONFIRM DELETION. THIS ACTION IS IRREVERSIBLE.")) return;
    try {
      await vendorsApi.deleteVendor(id);
      setData(prev => prev.filter(v => v.id !== id));
      toast.success('Vendor deleted');
    } catch (e) {
      toast.error(e.error || 'Deletion failed');
    }
  };

  const handleSave = async (formData) => {
    setIsSaving(true);
    try {
      if (editingRecord) {
        await vendorsApi.updateVendor(editingRecord.id, formData);
        toast.success('Vendor updated');
      } else {
        await vendorsApi.createVendor(formData);
        toast.success('Vendor created');
      }
      await fetchData(false);
      setIsModalOpen(false);
      setEditingRecord(null);
    } catch (e) {
      toast.error(e.error || 'Save failed');
    } finally {
      setIsSaving(false);
    }
  };

  const modalFields = [
    { name: 'vendor_name', label: 'Vendor Designation', required: true },
    { name: 'country_of_origin', label: 'Country of Origin' },
    { name: 'support_email', label: 'Support Email Address', type: 'email' },
    { name: 'support_phone', label: 'Support Contact Number' },
    { name: 'website', label: 'Corporate Website', type: 'url' },
  ];

  const columns = [
    {
      accessorKey: 'vendor_name',
      header: 'Manufacturer / Vendor',
      cell: (info) => {
        const vendor = info.row.original;
        const avatarUrl = `https://api.dicebear.com/7.x/initials/svg?seed=${vendor.vendor_name}&backgroundColor=0a0a0f`;
        return (
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded bg-surfaceHighlight border border-border p-1 overflow-hidden">
              <img src={avatarUrl} alt="avatar" className="w-full h-full object-cover" />
            </div>
            <div>
              <p className="font-bold text-textMain group-hover:text-primary transition-colors">{vendor.vendor_name}</p>
              <p className="text-xs text-textMuted flex items-center mt-0.5"><Globe size={10} className="mr-1"/> {vendor.country_of_origin || 'Unknown'}</p>
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: 'support_email',
      header: 'Support Email',
      cell: (info) => info.getValue() ? (
        <a href={`mailto:${info.getValue()}`} className="text-primary hover:neon-text flex items-center text-sm">
          <Mail size={12} className="mr-1.5" /> {info.getValue()}
        </a>
      ) : <span className="text-textMuted text-xs">N/A</span>,
    },
    {
      accessorKey: 'support_phone',
      header: 'Support Contact',
      cell: (info) => info.getValue() ? (
        <a href={`tel:${info.getValue()}`} className="text-textMain hover:text-primary flex items-center text-sm font-mono">
          <Phone size={12} className="mr-1.5" /> {info.getValue()}
        </a>
      ) : <span className="text-textMuted text-xs">N/A</span>,
    },
    {
      accessorKey: 'website',
      header: 'Portal',
      cell: (info) => info.getValue() ? (
        <a href={info.getValue()} target="_blank" rel="noopener noreferrer" className="text-info hover:neon-text text-sm hover:underline">
          Visit Site
        </a>
      ) : <span className="text-textMuted text-xs">N/A</span>,
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
          <p className="text-textMuted mt-1 font-mono text-sm uppercase">Vendor & Manufacturer Database</p>
        </div>
        
        <div className="flex items-center space-x-4 w-full md:w-auto">
          <div className="relative flex-1 md:w-72">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-primary">
              <Search size={18} />
            </div>
            <input
              type="text"
              value={globalFilter ?? ''}
              onChange={e => setGlobalFilter(e.target.value)}
              className="w-full bg-surface/50 backdrop-blur-md border border-primary/30 rounded-lg py-2 pl-10 pr-4 text-textMain focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary shadow-[0_0_15px_rgba(0,240,255,0.1)] transition-all placeholder-textMuted/50 font-mono text-sm"
              placeholder="Search vendors..."
            />
          </div>
          <Button variant="primary" onClick={() => { setEditingRecord(null); setIsModalOpen(true); }} className="shrink-0 flex items-center shadow-[0_0_10px_rgba(0,240,255,0.4)]">
            <Plus size={18} className="mr-2" />
            REGISTER VENDOR
          </Button>
        </div>
      </div>

      <div className="flex-1 min-h-0">
        <DataTable columns={columns} data={data} loading={loading} globalFilter={globalFilter} setGlobalFilter={setGlobalFilter}
          onEdit={(record) => { setEditingRecord(record); setIsModalOpen(true); }}
          onDelete={handleDelete} />
      </div>

      <DataModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} onSave={handleSave}
        title={editingRecord ? "MODIFY VENDOR PROFILE" : "REGISTER NEW VENDOR"}
        fields={modalFields} initialData={editingRecord} isSaving={isSaving} />
    </motion.div>
  );
}
