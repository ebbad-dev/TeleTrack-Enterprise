import apiClient from './client';

export const networkApi = {
  getLinks: () => apiClient.get('/network-links'),
};
