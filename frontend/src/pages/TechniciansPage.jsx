import React, { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Search, Users, Plus, Mail, Phone, Calendar } from 'lucide-react';
import { techniciansApi } from '../api';
import { extractItems } from '../api/helpers';
import { DataTable } from '../components/ui/DataTable';
import { Badge } from '../components/ui/Badge';
import { DataModal } from '../components/ui/DataModal';
import { Button } from '../components/ui/Button';
import useToastStore from '../store/toastStore';

export function TechniciansPage() {
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
      const res = await techniciansApi.getTechnicians();
      setData(extractItems(res));
    } catch (error) {
      console.error('Failed to fetch technicians', error);
      toast.error('Failed to load personnel data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData(true);
  }, [fetchData]);

  const handleDelete = async (id) => {
    if (!window.confirm("CONFIRM DISMISSAL. THIS ACTION IS IRREVERSIBLE.")) return;
    try {
      await techniciansApi.deleteTechnician(id);
      setData(prev => prev.filter(t => t.id !== id));
      toast.success('Personnel record archived');
    } catch (e) {
      toast.error(e.error || 'Action failed');
    }
  };

  const handleSave = async (formData) => {
    setIsSaving(true);
    try {
      if (editingRecord) {
        await techniciansApi.updateTechnician(editingRecord.id, formData);
        toast.success('Personnel record updated');
      } else {
        await techniciansApi.createTechnician(formData);
        toast.success('Personnel record created');
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
    { name: 'full_name', label: 'Operative Designation (Full Name)', required: true },
    { name: 'email', label: 'Comm Link (Email)', type: 'email', required: true },
    { name: 'phone', label: 'Direct Line (Phone)' },
    { name: 'specialization', label: 'Technical Specialization', type: 'select', required: true, options: [
      { value: 'Network Security', label: 'Network Security' },
      { value: 'Cloud Infrastructure', label: 'Cloud Infrastructure' },
      { value: 'Optical Fiber', label: 'Optical Fiber' },
      { value: 'Wireless Networks', label: 'Wireless Networks' },
      { value: 'Data Center Ops', label: 'Data Center Ops' },
      { value: 'VoIP Systems', label: 'VoIP Systems' },
    ]},
    { name: 'shift', label: 'Duty Cycle (Shift)', type: 'select', required: true, options: [
      { value: 'Morning', label: 'Morning Cycle' },
      { value: 'Evening', label: 'Evening Cycle' },
      { value: 'Night', label: 'Night Cycle' },
      { value: 'Flexible', label: 'Flexible Cycle' },
    ]},
    { name: 'status', label: 'Current Status', type: 'select', required: true, options: [
      { value: 'available', label: 'Available' },
      { value: 'busy', label: 'Engaged' },
      { value: 'on_leave', label: 'Off-Duty' },
    ]},
  ];

  const columns = [
    {
      accessorKey: 'full_name',
      header: 'Operative',
      cell: (info) => {
        const tech = info.row.original;
        const avatarUrl = `https://api.dicebear.com/7.x/avataaars/svg?seed=${tech.full_name}&backgroundColor=0a0a0f`;
        return (
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded-full bg-surfaceHighlight border-2 p-0.5 overflow-hidden shadow-[0_0_10px_rgba(0,0,0,0.5)] ${tech.status === 'available' ? 'border-success/50' : tech.status === 'busy' ? 'border-warning/50' : 'border-textMuted/50'}`}>
              <img src={avatarUrl} alt="avatar" className="w-full h-full object-cover rounded-full" />
            </div>
            <div>
              <p className="font-bold text-textMain group-hover:text-primary transition-colors">{tech.full_name}</p>
              <p className="text-xs text-textMuted font-mono flex items-center mt-0.5">
                <Mail size={10} className="mr-1" /> {tech.email}
              </p>
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: 'specialization',
      header: 'Specialization',
      cell: (info) => <span className="font-mono text-xs text-primary/90 tracking-wider">{info.getValue()?.toUpperCase()}</span>,
    },
    {
      accessorKey: 'shift',
      header: 'Duty Cycle',
      cell: (info) => (
        <div className="flex items-center text-xs font-mono text-textMuted">
          <Calendar size={12} className="mr-1.5" />
          {info.getValue()?.toUpperCase()}
        </div>
      ),
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: (info) => {
        const status = info.getValue();
        return (
          <Badge variant={status === 'available' ? 'success' : status === 'busy' ? 'warning' : 'default'}>
            {status?.replace('_', ' ').toUpperCase()}
          </Badge>
        );
      },
    },
    {
      accessorKey: 'phone',
      header: 'Comm Channel',
      cell: (info) => info.getValue() ? (
        <a href={`tel:${info.getValue()}`} className="text-textMuted hover:text-primary flex items-center text-xs font-mono transition-colors">
          <Phone size={12} className="mr-1.5" /> {info.getValue()}
        </a>
      ) : <span className="text-textMuted text-xs">OFFLINE</span>,
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
          <p className="text-textMuted mt-1 font-mono text-sm uppercase">Engineering Personnel Matrix</p>
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
              placeholder="Search personnel..."
            />
          </div>
          <Button variant="primary" onClick={() => { setEditingRecord(null); setIsModalOpen(true); }} className="shrink-0 flex items-center shadow-[0_0_10px_rgba(0,240,255,0.4)]">
            <Plus size={18} className="mr-2" />
            ONBOARD TECH
          </Button>
        </div>
      </div>

      <div className="flex-1 min-h-0">
        <DataTable columns={columns} data={data} loading={loading} globalFilter={globalFilter} setGlobalFilter={setGlobalFilter}
          onEdit={(record) => { setEditingRecord(record); setIsModalOpen(true); }}
          onDelete={handleDelete} />
      </div>

      <DataModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} onSave={handleSave}
        title={editingRecord ? "UPDATE DOSSIER" : "ONBOARD NEW OPERATIVE"}
        fields={modalFields} initialData={editingRecord} isSaving={isSaving} />
    </motion.div>
  );
}
