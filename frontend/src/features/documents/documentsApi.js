import api from '../../lib/axios';

export const documentsApi = {
    uploadDocument: async (file, onUploadProgress) => {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await api.post('/documents', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            onUploadProgress,
        });
        return response.data;
    },
    
    listDocuments: async () => {
        const response = await api.get('/documents');
        return response.data;
    },
    
    getDocument: async (id) => {
        const response = await api.get(`/documents/${id}`);
        return response.data;
    },

    getChunks: async (id) => {
        const response = await api.get(`/documents/${id}/chunks`);
        return response.data;
    },
    
    deleteDocument: async (id) => {
        const response = await api.delete(`/documents/${id}`);
        return response.data;
    }
};
