import { useMutation } from '@tanstack/react-query';
import { authApi } from './authApi';
import { useAuthStore } from '../../store/authStore';
import { useNavigate } from 'react-router-dom';

export const useAuth = () => {
    const { setAuth, clearAuth } = useAuthStore();
    const navigate = useNavigate();

    const loginMutation = useMutation({
        mutationFn: authApi.login,
        onSuccess: async (data) => {
            if (data.success) {
                // Fetch user info after successful login
                // We'll set the token first, so the getMe call uses it
                useAuthStore.setState({ 
                    accessToken: data.data.access_token, 
                    refreshToken: data.data.refresh_token,
                    isAuthenticated: true 
                });
                
                try {
                    const userResponse = await authApi.getMe();
                    if (userResponse.success) {
                        setAuth(userResponse.data, data.data.access_token, data.data.refresh_token);
                        navigate('/dashboard');
                    }
                } catch (error) {
                    clearAuth();
                    throw error;
                }
            }
        },
    });

    const registerMutation = useMutation({
        mutationFn: authApi.register,
        onSuccess: (data) => {
            if (data.success) {
                // Registration successful, could auto-login here or redirect to login
                navigate('/login');
            }
        },
    });

    const logoutMutation = useMutation({
        mutationFn: authApi.logout,
        onMutate: () => {
            clearAuth();
            navigate('/login');
        }
    });

    return {
        login: loginMutation,
        register: registerMutation,
        logout: logoutMutation
    };
};
