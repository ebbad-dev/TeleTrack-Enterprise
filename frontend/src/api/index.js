import apiClient from './client';

export const dashboardApi = {
  getSummary: () => apiClient.get('/dashboard/summary'),
  getAlertsBySeverity: () => apiClient.get('/dashboard/alerts-by-severity'),
  getDevicesByStatus: () => apiClient.get('/dashboard/devices-by-status'),
  getDevicesByType: () => apiClient.get('/dashboard/devices-by-type'),
  getRecentAlerts: () => apiClient.get('/dashboard/recent-alerts'),
  getAlertTrends: (days) => apiClient.get('/dashboard/alert-trends', { params: { days } }),
  getIncidentsBySeverity: () => apiClient.get('/dashboard/incidents-by-severity'),
  getSLAMetrics: () => apiClient.get('/dashboard/sla-metrics'),
};

export const devicesApi = {
  getDevices: (params) => apiClient.get('/devices', { params }),
  getDevice: (id) => apiClient.get(`/devices/${id}`),
  createDevice: (data) => apiClient.post('/devices', data),
  updateDevice: (id, data) => apiClient.put(`/devices/${id}`, data),
  deleteDevice: (id) => apiClient.delete(`/devices/${id}`),
  getDeviceMetrics: (id, params) => apiClient.get(`/devices/${id}/metrics`, { params }),
  discover: (data) => apiClient.post('/devices/discover', data),
};

export const alertsApi = {
  getAlerts: (params) => apiClient.get('/alerts', { params }),
  createAlert: (data) => apiClient.post('/alerts', data),
  updateAlert: (id, data) => apiClient.put(`/alerts/${id}`, data),
  deleteAlert: (id) => apiClient.delete(`/alerts/${id}`),
};

export const filesApi = {
  upload: (formData) => apiClient.post('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getIncidentFiles: (incidentId) => apiClient.get(`/files/incident/${incidentId}`),
  downloadAttachment: (attachmentId, filename) => 
    downloadFile(`/files/download/${attachmentId}`, filename),
};

const downloadFile = async (url, filename) => {
  try {
    const res = await apiClient.get(url, { responseType: 'blob' });
    const blob = new Blob([res]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
  } catch (error) {
    console.error('Download failed', error);
    alert('DOWNLOAD FAILED. CHECK SYSTEM LOGS.');
  }
};

export const exportApi = {
  exportDevices: (format = 'csv') => 
    downloadFile(`/export/devices?format=${format}`, `teletrack_devices.${format}`),
  exportAlerts: (params, format = 'csv') => {
    const query = new URLSearchParams({...params, format}).toString();
    downloadFile(`/export/alerts?${query}`, `teletrack_alerts.${format}`);
  },
  exportIncidents: (format = 'csv') => 
    downloadFile(`/export/incidents?format=${format}`, `teletrack_incidents.${format}`),
  exportAuditLogs: (format = 'csv') => 
    downloadFile(`/export/audit-logs?format=${format}`, `teletrack_audit_logs.${format}`),
};

export { networkApi } from './network';
export * from './crud';
