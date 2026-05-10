import React, { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Search, PenTool, Plus, Calendar, Clock } from 'lucide-react';
import { maintenanceApi, dropdownsApi } from '../api';
import { extractItems } from '../api/helpers';
import { DataTable } from '../components/ui/DataTable';
import { Badge } from '../components/ui/Badge';
import { DataModal } from '../components/ui/DataModal';
import { Button } from '../components/ui/Button';
import useToastStore from '../store/toastStore';

export function MaintenancePage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [globalFilter, setGlobalFilter] = useState('');
  
  const [devices, setDevices] = useState([]);
  const [technicians, setTechnicians] = useState([]);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const toast = useToastStore;

  const fetchData = useCallback(async (showLoading = false) => {
    if (showLoading) setLoading(true);
    try {
      const [maintRes, devRes, techRes] = await Promise.all([
        maintenanceApi.getMaintenance(),
        dropdownsApi.getDevices(),
        dropdownsApi.getTechnicians()
      ]);
      setData(extractItems(maintRes));
      if (devRes.success) setDevices(devRes.data || []);
      if (techRes.success) setTechnicians(techRes.data || []);
    } catch (error) {
      console.error('Failed to fetch maintenance logs', error);
      toast.error('Failed to load maintenance records');
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
      await maintenanceApi.deleteMaintenance(id);
      setData(prev => prev.filter(m => m.id !== id));
      toast.success('Maintenance record deleted');
    } catch (e) {
      toast.error(e.error || 'Deletion failed');
    }
  };

  const handleSave = async (formData) => {
    setIsSaving(true);
    try {
      const payload = {
        ...formData,
        device_id: parseInt(formData.device_id),
        technician_id: formData.technician_id ? parseInt(formData.technician_id) : null,
      };

      if (editingRecord) {
        await maintenanceApi.updateMaintenance(editingRecord.id, payload);
        toast.success('Maintenance record updated');
      } else {
        await maintenanceApi.createMaintenance(payload);
        toast.success('Maintenance record created');
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
    { name: 'device_id', label: 'Target Device', type: 'select', required: true, options: devices.map(d => ({ value: d.id, label: d.label })) },
    { name: 'technician_id', label: 'Assigned Operative', type: 'select', options: technicians.map(t => ({ value: t.id, label: t.label })) },
    { name: 'maintenance_type', label: 'Operation Type', type: 'select', required: true, options: [
      { value: 'Preventive', label: 'Preventive Maintenance' },
      { value: 'Hardware Replacement', label: 'Hardware Replacement' },
      { value: 'Firmware Patch', label: 'Firmware Update / Patch' },
      { value: 'Configuration Change', label: 'Configuration Change' },
      { value: 'Emergency Repair', label: 'Emergency Repair' },
    ]},
    { name: 'description', label: 'Operation Details', type: 'textarea', required: true },
    { name: 'scheduled_date', label: 'Scheduled Date', type: 'datetime-local' },
    { name: 'completed_date', label: 'Completion Date', type: 'datetime-local' },
    { name: 'outcome', label: 'Outcome Status', type: 'select', required: true, options: [
      { value: 'Success', label: 'Success' },
      { value: 'Failed', label: 'Failed' },
      { value: 'Pending', label: 'Pending / In Progress' },
    ]},
  ];

  const columns = [
    {
      accessorKey: 'maintenance_type',
      header: 'Operation',
      cell: (info) => {
        const record = info.row.original;
        return (
          <div className="flex items-center space-x-3">
            <div className={`w-8 h-8 rounded bg-surfaceHighlight border flex items-center justify-center ${record.outcome === 'Success' ? 'border-success text-success' : record.outcome === 'Failed' ? 'border-error text-error' : 'border-warning text-warning'}`}>
              <PenTool size={16} />
            </div>
            <div>
              <p className="font-bold text-textMain group-hover:text-primary transition-colors">{record.maintenance_type}</p>
              <p className="text-xs text-textMuted max-w-[200px] truncate">{record.description}</p>
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: 'device.device_name',
      header: 'Target Node',
      cell: (info) => <span className="font-mono text-xs text-textMain">{info.getValue() || `ID-${info.row.original.device_id}`}</span>,
    },
    {
      accessorKey: 'technician.full_name',
      header: 'Operative',
      cell: (info) => <span className="text-xs text-textMuted">{info.getValue() || 'UNASSIGNED'}</span>,
    },
    {
      accessorKey: 'completed_date',
      header: 'Completion',
      cell: (info) => {
        const val = info.getValue();
        if (!val) return <span className="text-xs text-warning font-mono">PENDING</span>;
        return (
          <div className="flex items-center text-xs text-textMuted font-mono">
            <Calendar size={12} className="mr-1.5" />
            {new Date(val).toLocaleDateString()}
          </div>
        );
      },
    },
    {
      accessorKey: 'outcome',
      header: 'Result',
      cell: (info) => {
        const outcome = info.getValue();
        return (
          <Badge variant={outcome === 'Success' ? 'success' : outcome === 'Failed' ? 'error' : 'warning'}>
            {outcome?.toUpperCase()}
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
          <h1 className="text-3xl font-bold text-textMain tracking-wide">SYSTEM <span className="text-info neon-text">MAINTENANCE</span></h1>
          <p className="text-textMuted mt-1 font-mono text-sm uppercase">Hardware & Firmware Operations</p>
        </div>
        
        <div className="flex items-center space-x-4 w-full md:w-auto">
          <div className="relative flex-1 md:w-72">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-info">
              <Search size={18} />
            </div>
            <input
              type="text"
              value={globalFilter ?? ''}
              onChange={e => setGlobalFilter(e.target.value)}
              className="w-full bg-surface/50 backdrop-blur-md border border-info/30 rounded-lg py-2 pl-10 pr-4 text-textMain focus:outline-none focus:border-info focus:ring-1 focus:ring-info shadow-[0_0_15px_rgba(0,145,168,0.1)] transition-all placeholder-textMuted/50 font-mono text-sm"
              placeholder="Search logs..."
            />
          </div>
          <Button variant="primary" onClick={() => { setEditingRecord(null); setIsModalOpen(true); }} className="shrink-0 flex items-center shadow-[0_0_10px_rgba(0,240,255,0.4)]">
            <Plus size={18} className="mr-2" />
            LOG OPERATION
          </Button>
        </div>
      </div>

      <div className="flex-1 min-h-0">
        <DataTable columns={columns} data={data} loading={loading} globalFilter={globalFilter} setGlobalFilter={setGlobalFilter}
          onEdit={(record) => { setEditingRecord(record); setIsModalOpen(true); }}
          onDelete={handleDelete} />
      </div>

      <DataModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} onSave={handleSave}
        title={editingRecord ? "MODIFY MAINTENANCE LOG" : "NEW MAINTENANCE LOG"}
        fields={modalFields} initialData={editingRecord} isSaving={isSaving} />
    </motion.div>
  );
}
