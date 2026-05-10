import React, { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Search, Plus } from 'lucide-react';
import { devicesApi, exportApi } from '../api';
import { DataTable } from '../components/ui/DataTable';
import { Badge } from '../components/ui/Badge';
import { DataModal } from '../components/ui/DataModal';
import { Button } from '../components/ui/Button';

export function DevicesPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [globalFilter, setGlobalFilter] = useState('');
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  const fetchData = useCallback(async (showLoading = false) => {
    if (showLoading) setLoading(true);
    try {
      const res = await devicesApi.getDevices();
      if (res.success && res.data) setData(res.data);
    } catch (error) {
      console.error('Failed to fetch devices', error);
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
      await devicesApi.deleteDevice(id);
      setData(prev => prev.filter(d => d.id !== id));
    } catch (e) {
      console.error(e);
      alert("Deletion failed.");
    }
  };

  const handleSave = async (formData) => {
    setIsSaving(true);
    try {
      if (editingRecord) {
        await devicesApi.updateDevice(editingRecord.id, formData);
      } else {
        await devicesApi.createDevice(formData);
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
    { name: 'device_name', label: 'Device Name', required: true },
    { name: 'device_type', label: 'Device Type', type: 'select', required: true, options: [
      { value: 'Router', label: 'Router' },
      { value: 'Switch', label: 'Switch' },
      { value: 'Server', label: 'Server' },
      { value: 'Firewall', label: 'Firewall' },
      { value: 'Storage', label: 'Storage' }
    ]},
    { name: 'ip_address', label: 'IP Address', required: true },
    { name: 'status', label: 'Operational Status', type: 'select', required: true, options: [
      { value: 'online', label: 'Online' },
      { value: 'offline', label: 'Offline' },
      { value: 'warning', label: 'Warning' }
    ]},
    { name: 'location_id', label: 'Location ID (Optional)' },
  ];

  const columns = [
    {
      accessorKey: 'device_name',
      header: 'Hardware Identification',
      cell: (info) => {
        const device = info.row.original;
        const avatarUrl = `https://api.dicebear.com/7.x/bottts/svg?seed=${device.device_name}&backgroundColor=0a0a0f`;
        return (
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded bg-surfaceHighlight border p-0.5 overflow-hidden shadow-md transition-colors ${device.status === 'online' ? 'border-primary/50' : device.status === 'offline' ? 'border-error/50' : 'border-warning/50'}`}>
              <img src={avatarUrl} alt="avatar" className="w-full h-full object-cover" />
            </div>
            <div>
              <p className="font-bold text-textMain group-hover:text-primary transition-colors">{device.device_name}</p>
              <p className="text-xs text-textMuted font-mono">{device.ip_address}</p>
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: 'device_type',
      header: 'Classification',
      cell: (info) => <span className="font-mono text-xs uppercase text-primary/80">{info.getValue()}</span>,
    },
    {
      accessorKey: 'status',
      header: 'Operational Status',
      cell: (info) => {
        const status = info.getValue();
        return (
          <Badge variant={status === 'online' ? 'success' : status === 'offline' ? 'error' : 'warning'}>
            {status.toUpperCase()}
          </Badge>
        );
      },
    },
    {
      accessorKey: 'last_seen',
      header: 'Last Telemetry',
      cell: (info) => {
        const date = info.getValue() ? new Date(info.getValue()) : null;
        return date ? (
          <span className="font-mono text-xs text-textMuted">{date.toLocaleString()}</span>
        ) : (
          <span className="font-mono text-xs text-textMuted/50">NO SIGNAL</span>
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
          <h1 className="text-3xl font-bold text-textMain tracking-wide">NETWORK <span className="text-primary neon-text">DEVICES</span></h1>
          <p className="text-textMuted mt-1 font-mono text-sm uppercase">Infrastructure Registry</p>
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
              placeholder="Search devices..."
            />
          </div>
          <div className="flex items-center space-x-2">
            <Button 
              variant="ghost" 
              onClick={() => {
                const subnet = window.prompt("ENTER TARGET SUBNET (CIDR):", "192.168.1.0/24");
                if (subnet) {
                  devicesApi.discover({ subnet }).then(res => {
                    if (res.success) alert("SCAN INITIALIZED. CHECK NOTIFICATIONS FOR RESULTS.");
                  });
                }
              }} 
              className="shrink-0 flex items-center border border-primary/30 hover:border-primary/60 text-primary/80"
            >
              SCAN NETWORK
            </Button>
            <Button variant="primary" onClick={openCreateModal} className="shrink-0 flex items-center shadow-[0_0_10px_rgba(0,240,255,0.4)]">
              <Plus size={18} className="mr-2" />
              NEW DEVICE
            </Button>
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
          onEdit={openEditModal}
          onDelete={handleDelete}
          onExport={(format) => exportApi.exportDevices(format)}
        />
      </div>

      <DataModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSave}
        title={editingRecord ? "MODIFY DEVICE RECORD" : "INITIALIZE NEW DEVICE"}
        fields={modalFields}
        initialData={editingRecord}
        isSaving={isSaving}
      />
    </motion.div>
  );
}
