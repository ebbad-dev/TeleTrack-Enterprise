import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Flame, Paperclip, Upload, X, Download as DownloadIcon, Loader2 } from 'lucide-react';
import { incidentsApi, exportApi, filesApi } from '../api';
import { DataTable } from '../components/ui/DataTable';
import { Badge } from '../components/ui/Badge';
import { DataModal } from '../components/ui/DataModal';
import { format } from 'date-fns';

export function IncidentsPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [globalFilter, setGlobalFilter] = useState('');
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [attachments, setAttachments] = useState([]);
  const [isUploading, setIsUploading] = useState(false);

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

  useEffect(() => {
    fetchData();
  }, []);

  const fetchAttachments = async (incidentId) => {
    try {
      const res = await filesApi.getIncidentFiles(incidentId);
      if (res.success) setAttachments(res.data);
    } catch (error) {
      console.error('Failed to fetch attachments', error);
    }
  };

  useEffect(() => {
    if (selectedIncident) {
      fetchAttachments(selectedIncident.id);
    } else {
      setAttachments([]);
    }
  }, [selectedIncident]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || !selectedIncident) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('incident_id', selectedIncident.id);

    setIsUploading(true);
    try {
      const res = await filesApi.upload(formData);
      if (res.success) {
        setAttachments(prev => [...prev, res.data]);
      }
    } catch (error) {
      console.error('Upload failed', error);
      alert('Upload failed: ' + (error.response?.data?.error || error.message));
    } finally {
      setIsUploading(false);
    }
  };

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
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setSelectedIncident(inc)}>
            <div className={`w-8 h-8 rounded bg-surfaceHighlight border flex items-center justify-center ${inc.severity === 'critical' ? 'border-error text-error' : 'border-warning text-warning'}`}>
              <Flame size={16} />
            </div>
            <div>
              <p className="font-bold text-textMain hover:text-primary transition-colors">{inc.title}</p>
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
          onExport={(format) => exportApi.exportIncidents(format)}
          onEdit={(inc) => setSelectedIncident(inc)}
        />
      </div>

      {selectedIncident && (
        <DataModal 
          isOpen={!!selectedIncident} 
          onClose={() => setSelectedIncident(null)}
          title={`INCIDENT DETAILS: ${selectedIncident.title}`}
        >
          <div className="space-y-6 text-textMain">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-textMuted uppercase font-mono mb-1">Status</p>
                <Badge variant={selectedIncident.status === 'resolved' ? 'success' : 'error'}>{selectedIncident.status.toUpperCase()}</Badge>
              </div>
              <div>
                <p className="text-xs text-textMuted uppercase font-mono mb-1">Severity</p>
                <Badge variant={selectedIncident.severity === 'critical' ? 'error' : 'warning'}>{selectedIncident.severity.toUpperCase()}</Badge>
              </div>
            </div>

            <div>
              <p className="text-xs text-textMuted uppercase font-mono mb-2">Description</p>
              <div className="bg-surfaceHighlight p-3 rounded border border-border text-sm italic">
                "{selectedIncident.description}"
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-textMuted uppercase font-mono">EVIDENCE & ATTACHMENTS</p>
                <label className="flex items-center space-x-1 text-xs text-primary hover:neon-text transition-all font-mono cursor-pointer">
                  {isUploading ? <Loader2 size={14} className="animate-spin" /> : <Upload size={14} />}
                  <span>{isUploading ? 'UPLOADING...' : 'UPLOAD FILE'}</span>
                  <input type="file" className="hidden" onChange={handleFileUpload} disabled={isUploading} />
                </label>
              </div>
              
              {attachments.length > 0 ? (
                <div className="grid grid-cols-1 gap-2">
                  {attachments.map(file => (
                    <div key={file.id} className="flex items-center justify-between p-2 bg-surfaceHighlight rounded border border-border/50 group hover:border-primary/50 transition-colors">
                      <div className="flex items-center space-x-2 overflow-hidden">
                        <Paperclip size={14} className="text-textMuted" />
                        <span className="text-xs font-mono truncate">{file.original_filename}</span>
                        <span className="text-[10px] text-textMuted">({(file.file_size / 1024).toFixed(1)} KB)</span>
                      </div>
                      <button 
                        onClick={() => filesApi.downloadAttachment(file.id, file.original_filename)} 
                        className="p-1.5 text-textMuted hover:text-primary transition-colors"
                        title="Download Evidence"
                      >
                        <DownloadIcon size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="border-2 border-dashed border-border rounded-lg p-8 flex flex-col items-center justify-center text-textMuted space-y-2 hover:border-primary/50 transition-colors cursor-pointer" onClick={() => document.querySelector('input[type="file"]').click()}>
                  <Paperclip size={24} />
                  <p className="text-xs font-mono">Drag evidence files here or click to scan...</p>
                </div>
              )}
            </div>

            <div className="flex justify-end">
              <button 
                onClick={() => setSelectedIncident(null)}
                className="px-4 py-2 bg-surfaceHighlight border border-border rounded text-xs font-mono hover:bg-border transition-colors"
              >
                CLOSE TERMINAL
              </button>
            </div>
          </div>
        </DataModal>
      )}
    </motion.div>
  );
}
