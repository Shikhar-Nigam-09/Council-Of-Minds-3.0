import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { conversationApi } from './conversationApi';

export const useConversation = (conversationId) => {
    return useQuery({
        queryKey: ['conversation', conversationId],
        queryFn: () => conversationApi.getConversation(conversationId),
        enabled: !!conversationId,
        refetchOnWindowFocus: false,
        refetchOnReconnect: false
    });
};

export const useCreateConversation = () => {
    return useMutation({
        mutationFn: (documentId) => conversationApi.createConversation(documentId),
    });
};

export const useStartTurn = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ conversationId, question }) => conversationApi.startTurn(conversationId, question),
        onMutate: async ({ conversationId, question }) => {
            await queryClient.cancelQueries({ queryKey: ['conversation', conversationId] });
            const previousConv = queryClient.getQueryData(['conversation', conversationId]);
            
            queryClient.setQueryData(['conversation', conversationId], old => {
                if (!old?.messages) return old;
                
                const optimisticMsg = {
                    id: `temp-${Date.now()}`,
                    role: 'user',
                    content: question,
                    final_answer: null,
                    status: 'awaiting_confirmation',
                    created_at: new Date().toISOString()
                };
                
                return {
                    ...old,
                    messages: [...old.messages, optimisticMsg]
                };
            });
            
            return { previousConv };
        },
        onError: (err, variables, context) => {
            queryClient.setQueryData(['conversation', variables.conversationId], context.previousConv);
        },
        onSettled: (_, error, variables) => {
            queryClient.invalidateQueries({ queryKey: ['conversation', variables.conversationId] });
        }
    });
};

export const useGetConfiguration = (conversationId, messageId) => {
    return useQuery({
        queryKey: ['configuration', conversationId, messageId],
        queryFn: () => conversationApi.getConfiguration(conversationId, messageId),
        enabled: !!conversationId && !!messageId && !String(messageId).startsWith('temp-'),
        refetchOnWindowFocus: false,
        refetchOnReconnect: false
    });
};

export const useConfirmTurn = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ conversationId, messageId, config }) => 
            conversationApi.confirmTurn(conversationId, messageId, config),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['conversation', variables.conversationId] });
            queryClient.invalidateQueries({ queryKey: ['configuration', variables.conversationId, variables.messageId] });
        }
    });
};

export const useGetAgentOutputs = (conversationId, messageId) => {
    return useQuery({
        queryKey: ['agent_outputs', conversationId, messageId],
        queryFn: () => conversationApi.getAgentOutputs(conversationId, messageId),
        enabled: !!conversationId && !!messageId && !String(messageId).startsWith('temp-'),
        refetchOnWindowFocus: false,
        refetchOnReconnect: false
    });
};
