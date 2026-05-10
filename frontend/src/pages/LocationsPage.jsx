import React, { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Search, MapPin, Plus } from 'lucide-react';
import { locationsApi } from '../api';
import { DataTable } from '../components/ui/DataTable';
import { Badge } from '../components/ui/Badge';
import { DataModal } from '../components/ui/DataModal';
import { Button } from '../components/ui/Button';

export function LocationsPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [globalFilter, setGlobalFilter] = useState('');

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  const fetchData = useCallback(async (showLoading = false) => {
    if (showLoading) setLoading(true);
    try {
      const res = await locationsApi.getLocations();
      if (res.success && res.data) {
        const items = res.data.items || (Array.isArray(res.data) ? res.data : []);
        setData(items);
      }
    } catch (error) {
      console.error('Failed to fetch locations', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData(true);
    const interval = setInterval(() => fetchData(false), 15000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleDelete = async (id) => {
    if (!window.confirm("CONFIRM DELETION. THIS ACTION IS IRREVERSIBLE.")) return;
    try {
      await locationsApi.deleteLocation(id);
      setData(prev => prev.filter(a => a.id !== id));
    } catch (e) {
      console.error(e);
      alert("Deletion failed.");
    }
  };

  const handleSave = async (formData) => {
    setIsSaving(true);
    try {
      if (editingRecord) {
        await locationsApi.updateLocation(editingRecord.id, formData);
      } else {
        await locationsApi.createLocation(formData);
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
    { name: 'location_name', label: 'Facility Designation', required: true },
    { name: 'site_type', label: 'Site Classification', type: 'select', required: true, options: [
      { value: 'Primary', label: 'Primary Datacenter' },
      { value: 'Secondary', label: 'Secondary Hub' },
      { value: 'Edge', label: 'Edge Node' },
      { value: 'Backup', label: 'Backup Facility' },
    ]},
    { name: 'address_line', label: 'Street Address', required: true },
    { name: 'city', label: 'City', required: true },
    { name: 'state_province', label: 'State/Province' },
    { name: 'postal_code', label: 'Postal Code' },
    { name: 'country', label: 'Country', required: true },
    { name: 'contact_person', label: 'Site Admin Name' },
    { name: 'contact_phone', label: 'Site Admin Phone' },
  ];

  const columns = [
    {
      accessorKey: 'location_name',
      header: 'Facility',
      cell: (info) => {
        const loc = info.row.original;
        const avatarUrl = `https://api.dicebear.com/7.x/identicon/svg?seed=${loc.location_name}&backgroundColor=0a0a0f`;
        return (
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded bg-surfaceHighlight border border-border p-1 overflow-hidden shadow-md">
              <img src={avatarUrl} alt="avatar" className="w-full h-full object-cover" />
            </div>
            <div>
              <p className="font-bold text-textMain group-hover:text-primary transition-colors">{loc.location_name}</p>
              <p className="text-xs text-textMuted flex items-center mt-0.5"><MapPin size={10} className="mr-1"/> {loc.city}, {loc.country}</p>
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: 'site_type',
      header: 'Classification',
      cell: (info) => <Badge variant="info">{info.getValue()?.toUpperCase()}</Badge>,
    },
    {
      accessorKey: 'contact_person',
      header: 'Site Admin',
      cell: (info) => (
        <div>
          <p className="text-sm font-medium">{info.getValue() || 'UNASSIGNED'}</p>
          <p className="text-xs text-textMuted font-mono">{info.row.original.contact_phone}</p>
        </div>
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
          <h1 className="text-3xl font-bold text-textMain tracking-wide">INFRASTRUCTURE <span className="text-primary neon-text">FACILITIES</span></h1>
          <p className="text-textMuted mt-1 font-mono text-sm uppercase">Global Location Directory</p>
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
              placeholder="Search facilities..."
            />
          </div>
          <Button variant="primary" onClick={openCreateModal} className="shrink-0 flex items-center shadow-[0_0_10px_rgba(0,240,255,0.4)]">
            <Plus size={18} className="mr-2" />
            NEW FACILITY
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
        />
      </div>

      <DataModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSave}
        title={editingRecord ? "MODIFY FACILITY RECORD" : "REGISTER NEW FACILITY"}
        fields={modalFields}
        initialData={editingRecord}
        isSaving={isSaving}
      />
    </motion.div>
  );
}
