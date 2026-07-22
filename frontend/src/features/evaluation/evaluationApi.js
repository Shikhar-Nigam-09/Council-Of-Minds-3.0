import api from '../../lib/axios';

export const evaluationApi = {
    runEvaluation: async (documentId, question) => {
        const response = await api.post('/evaluation/run', {
            document_id: documentId,
            question: question
        });
        return response.data;
    },
    listRuns: async (skip = 0, limit = 100) => {
        const response = await api.get('/evaluation/runs', {
            params: { skip, limit }
        });
        return response.data;
    },
    getRun: async (runId) => {
        const response = await api.get(`/evaluation/runs/${runId}`);
        return response.data;
    }
};
