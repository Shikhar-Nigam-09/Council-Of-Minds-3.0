import { useState, useCallback, useRef } from 'react';
import { useAuthStore } from '../../store/authStore';

export const useConversationStream = (conversationId, messageId) => {
    const [statuses, setStatuses] = useState({});
    const [answer, setAnswer] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);
    const [error, setError] = useState(null);
    const abortControllerRef = useRef(null);

    const startStream = useCallback(async () => {
        console.log(`[useConversationStream] startStream called for msg ${messageId}`);
        setIsStreaming(true);
        setError(null);
        setAnswer('');
        setStatuses({
            logical: 'pending',
            practical: 'pending',
            analytical: 'pending',
            skeptical: 'pending',
            ethics: 'pending'
        });

        abortControllerRef.current = new AbortController();
        const token = useAuthStore.getState().accessToken;

        try {
            const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
            console.log(`[useConversationStream] initiating fetch stream to ${baseUrl}/conversations/${conversationId}/messages/${messageId}/stream...`);
            const response = await fetch(`${baseUrl}/conversations/${conversationId}/messages/${messageId}/stream`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                signal: abortControllerRef.current.signal
            });

            if (!response.ok) {
                console.error(`[useConversationStream] Stream fetch failed with status: ${response.status}`);
                throw new Error(`Failed to connect to stream: ${response.statusText}`);
            }

            console.log(`[useConversationStream] fetch stream connected! reading body...`);
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let firstChunkReceived = false;

            while (true) {
                const { done, value } = await reader.read();
                if (done) {
                    console.log(`[useConversationStream] stream reader done.`);
                    break;
                }
                
                if (!firstChunkReceived) {
                    console.log(`[useConversationStream] First chunk received!`);
                    firstChunkReceived = true;
                }

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            if (data.type === 'agent_status') {
                                setStatuses(prev => ({ ...prev, [data.agent]: data.status }));
                            } else if (data.type === 'answer_chunk') {
                                setAnswer(prev => prev + data.content);
                            } else if (data.type === 'error') {
                                setError(data.message);
                            } else if (data.type === 'done') {
                                setIsStreaming(false);
                            }
                        } catch (e) {
                            console.error('Error parsing SSE data', e);
                        }
                    }
                }
            }
        } catch (e) {
            if (e.name !== 'AbortError') {
                setError(e.message);
                setIsStreaming(false);
            }
        }
    }, [conversationId, messageId]);

    const stopStream = useCallback(() => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            setIsStreaming(false);
        }
    }, []);

    return { statuses, answer, isStreaming, error, startStream, stopStream };
};
