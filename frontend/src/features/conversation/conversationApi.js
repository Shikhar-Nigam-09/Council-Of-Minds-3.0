import api from '../../lib/axios';

export const conversationApi = {
    createConversation: async (documentId) => {
        const response = await api.post(`/api/v1/conversations?document_id=${documentId}`);
        return response.data;
    },
    
    getConversation: async (id) => {
        const response = await api.get(`/api/v1/conversations/${id}`);
        return response.data;
    },
    
    startTurn: async (conversationId, question) => {
        const response = await api.post(`/api/v1/conversations/${conversationId}/messages`, {
            question
        });
        return response.data;
    },
    
    getConfiguration: async (conversationId, messageId) => {
        const response = await api.get(`/api/v1/conversations/${conversationId}/messages/${messageId}/configuration`);
        return response.data;
    },
    
    confirmTurn: async (conversationId, messageId, config) => {
        const response = await api.post(`/api/v1/conversations/${conversationId}/messages/${messageId}/confirm`, config);
        return response.data;
    },
    
    getAgentOutputs: async (conversationId, messageId) => {
        const response = await api.get(`/api/v1/conversations/${conversationId}/messages/${messageId}/agent-outputs`);
        return response.data;
    }
};
