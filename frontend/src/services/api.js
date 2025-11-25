import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getPublications = async (params = {}) => {
  const response = await api.get('/api/publications/', { params });
  return response.data;
};

export const searchPublications = async (query, limit = 20) => {
  const response = await api.get('/api/publications/search', {
    params: { q: query, limit }
  });
  return response.data;
};

export const getPublicationStats = async () => {
  const response = await api.get('/api/publications/stats');
  return response.data;
};

export const getPublicationById = async (id) => {
  const response = await api.get(`/api/publications/${id}`);
  return response.data;
};

export const getTopics = async () => {
  const response = await api.get('/api/topics/');
  return response.data;
};

export const getTopicTrends = async () => {
  const response = await api.get('/api/topics/trends');
  return response.data;
};

export default api;