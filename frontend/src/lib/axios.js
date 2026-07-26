import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '',
    headers: {
        'Content-Type': 'application/json'
    }
});

api.interceptors.request.use((config) => {
    const { accessToken } = useAuthStore.getState();
    if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
}, (error) => Promise.reject(error));

api.interceptors.response.use((response) => response, async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 429) {
        alert("Too many requests. Please try again later.");
        return Promise.reject(error);
    }
    
    if (error.response?.status === 402) {
        alert("Daily cost limit exceeded. Please try again tomorrow or upgrade your plan.");
        return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        const { refreshToken, clearAuth, setAuth } = useAuthStore.getState();
        if (refreshToken) {
            try {
                const res = await axios.post(`${import.meta.env.VITE_API_BASE_URL || ''}/api/v1/auth/refresh`, {
                    refresh_token: refreshToken
                });
                
                if (res.data.success) {
                    const { access_token, refresh_token } = res.data.data;
                    setAuth(
                        useAuthStore.getState().user,
                        access_token,
                        refresh_token
                    );
                    originalRequest.headers.Authorization = `Bearer ${access_token}`;
                    return api(originalRequest);
                }
            } catch (refreshError) {
                clearAuth();
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        } else {
            clearAuth();
            window.location.href = '/login';
        }
    }
    return Promise.reject(error);
});

export default api;
