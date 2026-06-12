import apiClient, { downloadFile } from './client';

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
  getAlert: (id) => apiClient.get(`/alerts/${id}`),
  createAlert: (data) => apiClient.post('/alerts', data),
  updateAlert: (id, data) => apiClient.put(`/alerts/${id}`, data),
  deleteAlert: (id) => apiClient.delete(`/alerts/${id}`),
  assignAlert: (id, data) => apiClient.post(`/alerts/${id}/assign`, data),
  resolveAlert: (id, data) => apiClient.post(`/alerts/${id}/resolve`, data),
  getComments: (id) => apiClient.get(`/alerts/${id}/comments`),
  addComment: (id, data) => apiClient.post(`/alerts/${id}/comments`, data),
};

export const filesApi = {
  upload: (formData) => apiClient.post('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getIncidentFiles: (incidentId) => apiClient.get(`/files/incident/${incidentId}`),
  downloadAttachment: (attachmentId, filename) => 
    downloadFile(`/files/download/${attachmentId}`, filename),
};

export const databaseApi = {
  getActiveDevicesView: () => apiClient.get('/database/views/active-devices'),
  getCriticalAlertsView: () => apiClient.get('/database/views/critical-alerts'),
  getOpenIncidentsView: () => apiClient.get('/database/views/open-incidents'),
  getTriggerHistory: () => apiClient.get('/database/triggers/status-history'),
  getProcedureStats: () => apiClient.get('/database/procedures/network-stats'),
  getPredictiveAnalytics: () => apiClient.get('/database/procedures/predictive-analytics'),
  getTimeTravel: (timestamp) => apiClient.get(`/database/time-travel?timestamp=${timestamp}`),
  getIndexes: () => apiClient.get('/database/indexes'),
  getIndexSample: (table, col) => apiClient.get(`/database/indexes/${table}/${col}`),
};

export const exportApi = {
  exportDevices: (format = 'csv') => 
    downloadFile(`/export/devices?format=${format}`, `teletrack_devices.${format}`),
  exportAlerts: (params = {}, format = 'csv') => {
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
