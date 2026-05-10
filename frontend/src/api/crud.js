import apiClient from './client';

export const techniciansApi = {
  getTechnicians: (params) => apiClient.get('/technicians', { params }),
  createTechnician: (data) => apiClient.post('/technicians', data),
  updateTechnician: (id, data) => apiClient.put(`/technicians/${id}`, data),
  deleteTechnician: (id) => apiClient.delete(`/technicians/${id}`),
};

export const locationsApi = {
  getLocations: (params) => apiClient.get('/locations', { params }),
  createLocation: (data) => apiClient.post('/locations', data),
  updateLocation: (id, data) => apiClient.put(`/locations/${id}`, data),
  deleteLocation: (id) => apiClient.delete(`/locations/${id}`),
};

export const vendorsApi = {
  getVendors: (params) => apiClient.get('/vendors', { params }),
  createVendor: (data) => apiClient.post('/vendors', data),
  updateVendor: (id, data) => apiClient.put(`/vendors/${id}`, data),
  deleteVendor: (id) => apiClient.delete(`/vendors/${id}`),
};

export const incidentsApi = {
  getIncidents: (params) => apiClient.get('/incidents', { params }),
  createIncident: (data) => apiClient.post('/incidents', data),
  updateIncident: (id, data) => apiClient.put(`/incidents/${id}`, data),
  deleteIncident: (id) => apiClient.delete(`/incidents/${id}`),
};

export const maintenanceApi = {
  getMaintenance: (params) => apiClient.get('/maintenance', { params }),
  createMaintenance: (data) => apiClient.post('/maintenance', data),
  updateMaintenance: (id, data) => apiClient.put(`/maintenance/${id}`, data),
  deleteMaintenance: (id) => apiClient.delete(`/maintenance/${id}`),
};

export const auditApi = {
  getLogs: (params) => apiClient.get('/audit-logs', { params }),
};

export const notificationsApi = {
  getNotifications: (params) => apiClient.get('/notifications', { params }),
  markRead: (id) => apiClient.put(`/notifications/${id}/read`),
};

export const searchApi = {
  globalSearch: (query) => apiClient.get('/search', { params: { q: query } }),
};

export const dropdownsApi = {
  getLocations: () => apiClient.get('/dropdowns/locations'),
  getTechnicians: () => apiClient.get('/dropdowns/technicians'),
  getVendors: () => apiClient.get('/dropdowns/vendors'),
  getDevices: () => apiClient.get('/dropdowns/devices'),
  getSLAPolicies: () => apiClient.get('/dropdowns/sla-policies'),
};
