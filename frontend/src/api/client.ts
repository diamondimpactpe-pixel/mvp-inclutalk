import axios from 'axios';
import { API_BASE_URL, API_V1_PREFIX } from '../utils/constants';
 

const client = axios.create({
  baseURL: API_BASE_URL + API_V1_PREFIX,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
});

client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log('Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

client.interceptors.response.use(
  (response) => {
    console.log('Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('Response error:', {
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url
    });
    
    if (error.response?.status === 401 && !error.config?.url?.includes('/login')) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

export default client;