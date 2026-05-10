import axios from 'axios';

// Create the axios instance
const apiClient = axios.create({
  baseURL: '/api', // Proxied by Vite to http://127.0.0.1:5000
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
  (response) => response.data,
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't already retried
    if (error.response?.status === 401 && !originalRequest._retry) {
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

export default apiClient;
