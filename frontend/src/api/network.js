import apiClient from './client';

export const networkApi = {
  getLinks: (params) => apiClient.get('/network-links', { params }),
  createLink: (data) => apiClient.post('/network-links', data),
  updateLink: (id, data) => apiClient.put(`/network-links/${id}`, data),
  deleteLink: (id) => apiClient.delete(`/network-links/${id}`),
};
