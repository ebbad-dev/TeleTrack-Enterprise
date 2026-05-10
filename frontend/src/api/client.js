import axios from 'axios';

// Create the axios instance
const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to inject the token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add a response interceptor to handle token refresh and 401s
apiClient.interceptors.response.use(
  (response) => {
    // For blob responses (file downloads), return the raw response
    if (response.config.responseType === 'blob') {
      return response;
    }
    return response.data;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't already retried
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Don't refresh on login route
      if (originalRequest.url.includes('/auth/login')) {
        return Promise.reject(error.response?.data || error);
      }
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }
        
        // Attempt to refresh the token
        const res = await axios.post('/api/auth/refresh', {}, {
          headers: {
            'Authorization': `Bearer ${refreshToken}`
          }
        });
        
        if (res.data?.success && res.data?.access_token) {
          localStorage.setItem('accessToken', res.data.access_token);
          // Retry the original request with the new token
          originalRequest.headers.Authorization = `Bearer ${res.data.access_token}`;
          const retryResponse = await axios(originalRequest);
          // Apply same parsing logic on retry
          if (originalRequest.responseType === 'blob') {
            return retryResponse;
          }
          return retryResponse.data;
        }
      } catch (refreshError) {
        // If refresh fails, clear tokens and redirect to login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error.response?.data || error);
  }
);

// Helper for downloading files (bypasses JSON interceptor)
export async function downloadFile(url, filename) {
  try {
    const token = localStorage.getItem('accessToken');
    const response = await axios.get(`/api${url}`, {
      responseType: 'blob',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    const blob = new Blob([response.data]);
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
    throw error;
  }
}

export default apiClient;
