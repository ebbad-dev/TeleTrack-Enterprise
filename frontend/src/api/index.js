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
  getDownloadUrl: (attachmentId) => `/api/files/download/${attachmentId}`,
};

export const exportApi = {
  exportDevices: (format = 'csv') => window.open(`/api/export/devices?format=${format}`, '_blank'),
  exportAlerts: (params, format = 'csv') => {
    const query = new URLSearchParams({...params, format}).toString();
    window.open(`/api/export/alerts?${query}`, '_blank');
  },
  exportIncidents: (format = 'csv') => window.open(`/api/export/incidents?format=${format}`, '_blank'),
  exportAuditLogs: (format = 'csv') => window.open(`/api/export/audit-logs?format=${format}`, '_blank'),
};

export { networkApi } from './network';
export * from './crud';
