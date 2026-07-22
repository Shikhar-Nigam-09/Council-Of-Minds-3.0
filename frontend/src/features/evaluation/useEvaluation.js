import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { evaluationApi } from './evaluationApi';

export const useEvaluationRuns = (skip = 0, limit = 100) => {
    return useQuery({
        queryKey: ['evaluationRuns', skip, limit],
        queryFn: () => evaluationApi.listRuns(skip, limit)
    });
};

export const useRunEvaluation = () => {
    const queryClient = useQueryClient();
    
    return useMutation({
        mutationFn: ({ documentId, question }) => evaluationApi.runEvaluation(documentId, question),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['evaluationRuns'] });
        }
    });
};
