import React, { useEffect, useState } from 'react';
import { useConversationStream } from '../../features/conversation/useConversationStream';
import { useGetAgentOutputs } from '../../features/conversation/useConversation';
import { CouncilProgress } from './CouncilProgress';
import { AgentOutputPanel } from './AgentOutputPanel';
import { useQueryClient } from '@tanstack/react-query';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Copy, Check, User, Bot, Loader2 } from 'lucide-react';

export const ConversationMessage = React.memo(function ConversationMessage({ message, conversationId, isLatest }) {
    const queryClient = useQueryClient();
    
    // For completed messages, fetch static outputs
    const { data: staticOutputs } = useGetAgentOutputs(conversationId, message.id);
    
    // For confirmed/active message, use streaming
    const { statuses, answer, isStreaming, error, startStream, stopStream } = useConversationStream(conversationId, message.id);
    
    const [finalOutputs, setFinalOutputs] = useState([]);
    const [copied, setCopied] = useState(false);
    
    const hasStartedRef = React.useRef(false);

    useEffect(() => {
        if (message.status === 'confirmed' && isLatest && !hasStartedRef.current) {
            console.log(`[ConversationMessage] Conditions met! Calling startStream()...`);
            hasStartedRef.current = true;
            startStream();
        }
    }, [message.status, isLatest, startStream]);
    
    useEffect(() => {
        return () => {
            console.log(`[ConversationMessage] Unmounting. Cleanup stopping stream!`);
            stopStream();
        };
    }, [stopStream]);
    
    useEffect(() => {
        if (message.status === 'confirmed' && !isStreaming && answer) {
            setTimeout(() => {
                queryClient.invalidateQueries({ queryKey: ['conversation', conversationId] });
            }, 1000);
        }
    }, [isStreaming, message.status, answer, queryClient, conversationId]);

    useEffect(() => {
        if (staticOutputs) {
            setFinalOutputs(staticOutputs);
        }
    }, [staticOutputs]);

    const completedStatuses = {};
    if (message.status === 'completed' && staticOutputs) {
        staticOutputs.forEach(out => {
            completedStatuses[out.agent_name] = out.status === 'success' ? 'complete' : 'failed';
        });
    }

    const currentAnswer = message.status === 'completed' ? message.final_answer : answer;
    const currentStatuses = message.status === 'completed' ? completedStatuses : statuses;

    const handleCopy = () => {
        navigator.clipboard.writeText(currentAnswer || message.content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="flex flex-col w-full">
            {/* User Question */}
            <div className="flex w-full py-6 px-4 md:px-6 lg:px-8 bg-white dark:bg-slate-900 border-b border-slate-100 dark:border-slate-800">
                <div className="max-w-4xl mx-auto w-full flex gap-4 md:gap-6">
                    <div className="shrink-0 flex flex-col items-center">
                        <div className="flex h-8 w-8 items-center justify-center rounded-sm bg-emerald-500 text-white shadow-sm">
                            <User className="h-5 w-5" />
                        </div>
                    </div>
                    <div className="flex-1 min-w-0 space-y-4 pt-1">
                        <span className="font-semibold text-slate-900 dark:text-white">You</span>
                        <div className="prose prose-slate dark:prose-invert max-w-none text-slate-800 dark:text-slate-200 text-sm md:text-base leading-relaxed whitespace-pre-wrap">
                            {message.content}
                        </div>
                    </div>
                </div>
            </div>

            {/* Assistant Response (Council) */}
            <div className="flex w-full py-6 px-4 md:px-6 lg:px-8 bg-slate-50 dark:bg-slate-800">
                <div className="max-w-4xl mx-auto w-full flex gap-4 md:gap-6">
                    <div className="shrink-0 flex flex-col items-center">
                        <div className="flex h-8 w-8 items-center justify-center rounded-sm bg-indigo-600 text-white shadow-sm">
                            <Bot className="h-5 w-5" />
                        </div>
                    </div>
                    <div className="flex-1 min-w-0 space-y-4 pt-1">
                        <div className="flex justify-between items-start">
                            <span className="font-semibold text-slate-900 dark:text-white">Council of Minds</span>
                            {currentAnswer && (
                                <button 
                                    onClick={handleCopy}
                                    className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
                                    title="Copy response"
                                >
                                    {copied ? <Check className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
                                </button>
                            )}
                        </div>

                        <div className="prose prose-slate dark:prose-invert max-w-none text-slate-800 dark:text-slate-200 text-sm md:text-base leading-relaxed">
                            <div className="space-y-6">
                                {/* Loading State */}
                                {message.status === 'awaiting_confirmation' && (
                                    <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 italic">
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                        Planner is analyzing...
                                    </div>
                                )}
                                
                                {/* Error State */}
                                {error && (
                                    <div className="bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 p-4 rounded-md text-sm border border-red-200 dark:border-red-800">
                                        <p className="mb-2">Error during generation: {error}</p>
                                        <button 
                                            onClick={startStream}
                                            className="px-3 py-1.5 bg-red-100 dark:bg-red-900/50 hover:bg-red-200 dark:hover:bg-red-800/50 rounded-md text-xs font-medium transition-colors"
                                        >
                                            Retry Connection
                                        </button>
                                    </div>
                                )}
                                
                                {/* Council Progress & Outputs */}
                                {(message.status === 'confirmed' || message.status === 'completed') && (
                                    <>
                                        <CouncilProgress statuses={currentStatuses} />
                                        
                                        {message.status === 'completed' && staticOutputs && staticOutputs.length > 0 && (
                                            <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
                                                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4">Council Reasoning</h4>
                                                <div className="space-y-2">
                                                    {staticOutputs.map(out => (
                                                        <AgentOutputPanel key={out.id} agentName={out.agent_name} output={out} />
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                        
                                        {/* Answer Output */}
                                        {(currentAnswer || isStreaming) && (
                                            <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
                                                {!currentAnswer && isStreaming ? (
                                                    <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 italic mb-2 text-sm">
                                                        <Loader2 className="h-4 w-4 animate-spin text-indigo-500" />
                                                        Council is thinking...
                                                    </div>
                                                ) : (
                                                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                        {currentAnswer || ''}
                                                    </ReactMarkdown>
                                                )}
                                                {isStreaming && currentAnswer && (
                                                    <span className="inline-block w-2 h-4 ml-1 bg-indigo-600 animate-pulse"></span>
                                                )}
                                            </div>
                                        )}
                                    </>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
});
