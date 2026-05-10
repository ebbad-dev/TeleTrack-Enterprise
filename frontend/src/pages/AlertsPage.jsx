import React, { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Search, ShieldAlert, Plus } from 'lucide-react';
import { alertsApi, devicesApi, exportApi } from '../api';
import { DataTable } from '../components/ui/DataTable';
import { Badge } from '../components/ui/Badge';
import { DataModal } from '../components/ui/DataModal';
import { Button } from '../components/ui/Button';

export function AlertsPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [globalFilter, setGlobalFilter] = useState('');
  const [devices, setDevices] = useState([]);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  const fetchData = useCallback(async (showLoading = false) => {
    if (showLoading) setLoading(true);
    try {
      const [alertRes, devRes] = await Promise.all([
        alertsApi.getAlerts(),
        devicesApi.getDevices()
      ]);
      if (alertRes.success) {
        const alertItems = alertRes.data.items || (Array.isArray(alertRes.data) ? alertRes.data : []);
        setData(alertItems);
      }
      if (devRes.success) {
        const devItems = devRes.data.items || (Array.isArray(devRes.data) ? devRes.data : []);
        setDevices(devItems);
      }
    } catch (error) {
      console.error('Failed to fetch alerts', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData(true);
    const interval = setInterval(() => fetchData(false), 10000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleDelete = async (id) => {
    if (!window.confirm("CONFIRM DELETION. THIS ACTION IS IRREVERSIBLE.")) return;
    try {
      await alertsApi.deleteAlert(id);
      setData(prev => prev.filter(a => a.id !== id));
    } catch (e) {
      console.error(e);
      alert("Deletion failed.");
    }
  };

  const handleSave = async (formData) => {
    setIsSaving(true);
    try {
      const payload = {
        ...formData,
        device_id: parseInt(formData.device_id)
      };

      if (editingRecord) {
        await alertsApi.updateAlert(editingRecord.id, payload);
      } else {
        await alertsApi.createAlert(payload);
      }
      await fetchData(false);
      setIsModalOpen(false);
      setEditingRecord(null);
    } catch (e) {
      console.error(e);
      alert("Save failed.");
    } finally {
      setIsSaving(false);
    }
  };

  const openCreateModal = () => {
    setEditingRecord(null);
    setIsModalOpen(true);
  };

  const openEditModal = (record) => {
    setEditingRecord(record);
    setIsModalOpen(true);
  };

  const modalFields = [
    { 
      name: 'device_id', 
      label: 'Target Device', 
      type: 'select', 
      required: true, 
      options: devices.map(d => ({ 
        value: d.id, 
        label: d.device_name ? `${d.device_name} (${d.ip_address || ''})` : d.label 
      }))
    },
    { name: 'message', label: 'Alert Message', type: 'textarea', required: true },
    { name: 'severity', label: 'Severity Level', type: 'select', required: true, options: [
      { value: 'critical', label: 'Critical' },
      { value: 'high', label: 'High' },
      { value: 'medium', label: 'Medium' },
      { value: 'low', label: 'Low' },
    ]},
    { name: 'status', label: 'Resolution Status', type: 'select', required: true, options: [
      { value: 'open', label: 'Open' },
      { value: 'acknowledged', label: 'Acknowledged' },
      { value: 'resolved', label: 'Resolved' },
    ]},
  ];

  const columns = [
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
      accessorKey: 'message',
      header: 'Threat Intel / Log',
      cell: (info) => {
        const alert = info.row.original;
        return (
          <div className="flex flex-col">
            <span className="font-bold text-textMain">{alert.message}</span>
            <span className="text-xs text-textMuted font-mono mt-1">DEVICE: {alert.device ? alert.device.device_name : `ID-${alert.device_id}`}</span>
          </div>
        );
      },
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: (info) => {
        const status = info.getValue();
        return (
          <span className={`font-mono text-xs uppercase tracking-widest ${status === 'resolved' ? 'text-success' : status === 'acknowledged' ? 'text-warning' : 'text-error'}`}>
            {status}
          </span>
        );
      },
    },
    {
      accessorKey: 'created_at',
      header: 'Timestamp',
      cell: (info) => <span className="font-mono text-xs text-textMuted">{new Date(info.getValue()).toLocaleString()}</span>,
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
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-error/10 border border-error/30 rounded-lg">
            <ShieldAlert size={28} className="text-error" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-textMain tracking-wide">THREAT <span className="text-error neon-text">ANALYSIS</span></h1>
            <p className="text-textMuted mt-1 font-mono text-sm uppercase">Active Alerts Log</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-4 w-full md:w-auto">
          <div className="relative flex-1 md:w-72">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-error">
              <Search size={18} />
            </div>
            <input
              type="text"
              value={globalFilter ?? ''}
              onChange={e => setGlobalFilter(e.target.value)}
              className="w-full bg-surface/50 backdrop-blur-md border border-error/30 rounded-lg py-2 pl-10 pr-4 text-textMain focus:outline-none focus:border-error focus:ring-1 focus:ring-error shadow-[0_0_15px_rgba(255,0,60,0.1)] transition-all placeholder-textMuted/50 font-mono text-sm"
              placeholder="Search threat logs..."
            />
          </div>
          <Button variant="danger" onClick={openCreateModal} className="shrink-0 flex items-center shadow-[0_0_10px_rgba(255,0,60,0.4)] hover:bg-error/80 bg-error text-white">
            <Plus size={18} className="mr-2" />
            INJECT LOG
          </Button>
        </div>
      </div>

      <div className="flex-1 min-h-0">
        <DataTable 
          columns={columns} 
          data={data} 
          loading={loading} 
          globalFilter={globalFilter} 
          setGlobalFilter={setGlobalFilter} 
          onEdit={openEditModal}
          onDelete={handleDelete}
          onExport={(format) => exportApi.exportAlerts({}, format)}
        />
      </div>

      <DataModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSave}
        title={editingRecord ? "MODIFY THREAT LOG" : "INJECT MANUAL THREAT LOG"}
        fields={modalFields}
        initialData={editingRecord}
        isSaving={isSaving}
      />
    </motion.div>
  );
}
