import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsApi } from './documentsApi';

export const useDocuments = () => {
    const queryClient = useQueryClient();

    const documentsListQuery = useQuery({
        queryKey: ['documents'],
        queryFn: documentsApi.listDocuments,
        staleTime: 5 * 60 * 1000,
        refetchOnWindowFocus: false,
        refetchOnReconnect: false
    });

    const uploadMutation = useMutation({
        mutationFn: ({ file, onUploadProgress }) => 
            documentsApi.uploadDocument(file, onUploadProgress),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['documents'] });
        },
    });

    const deleteMutation = useMutation({
        mutationFn: documentsApi.deleteDocument,
        onMutate: async (id) => {
            await queryClient.cancelQueries({ queryKey: ['documents'] });
            const previousDocs = queryClient.getQueryData(['documents']);
            queryClient.setQueryData(['documents'], old => {
                if (!old?.data) return old;
                return { ...old, data: old.data.filter(doc => doc.id !== id) };
            });
            return { previousDocs };
        },
        onError: (err, id, context) => {
            queryClient.setQueryData(['documents'], context.previousDocs);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['documents'] });
        },
    });

    const useDocumentDetail = (id) => {
        return useQuery({
            queryKey: ['document', id],
            queryFn: async () => {
                const [docRes, chunksRes] = await Promise.all([
                    documentsApi.getDocument(id),
                    documentsApi.getChunks(id)
                ]);
                return {
                    data: {
                        document: docRes.data,
                        chunks: chunksRes.data
                    }
                };
            },
            enabled: !!id,
            staleTime: 5 * 60 * 1000,
            refetchOnWindowFocus: false,
            refetchOnReconnect: false
        });
    };

    return {
        documents: documentsListQuery,
        upload: uploadMutation,
        deleteDocument: deleteMutation,
        useDocumentDetail
    };
};
