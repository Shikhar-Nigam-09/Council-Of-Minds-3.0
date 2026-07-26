import api from '../../lib/axios';

export const authApi = {
    login: async (credentials) => {
        const response = await api.post('/api/v1/auth/login', credentials);
        return response.data;
    },
    
    register: async (userData) => {
        const response = await api.post('/api/v1/auth/register', userData);
        return response.data;
    },
    
    logout: async () => {
        const response = await api.post('/api/v1/auth/logout');
        return response.data;
    },
    
    getMe: async () => {
        const response = await api.get('/api/v1/auth/me');
        return response.data;
    }
};
