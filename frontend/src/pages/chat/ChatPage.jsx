import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useDocuments } from '../../features/documents/useDocuments';
import { useConversation, useCreateConversation, useStartTurn, useConfirmTurn, useGetConfiguration } from '../../features/conversation/useConversation';
import { QuestionInput } from '../../components/conversation/QuestionInput';
import { CouncilWeightPanel } from '../../components/conversation/CouncilWeightPanel';
import { ConversationMessage } from '../../components/conversation/ConversationMessage';
import { MessageSquare, Bot, User, Loader2, Settings, FileText, ChevronDown, Check, Trash2, Copy } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useAuthStore } from '../../store/authStore';

const AGENT_PRESETS = {
    balanced: { logical: 20, practical: 20, analytical: 20, skeptical: 20, ethics: 20 },
    research: { logical: 30, practical: 10, analytical: 40, skeptical: 10, ethics: 10 },
    critical: { logical: 20, practical: 10, analytical: 20, skeptical: 40, ethics: 10 },
    creative: { logical: 10, practical: 20, analytical: 30, skeptical: 10, ethics: 30 }
};

export default function ChatPage() {
    const [searchParams, setSearchParams] = useSearchParams();
    const docIdParam = searchParams.get('docId');
    const convIdParam = searchParams.get('convId');
    const { documents } = useDocuments();
    
    // Filter completed documents to serve as context options
    const completedDocs = documents.data?.data?.filter(d => d.status === 'completed') || [];
    
    const [activeDocId, setActiveDocId] = useState(docIdParam || null);
    const [isGeneralMode, setIsGeneralMode] = useState(false);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);

    // If there are zero indexed documents, default to General mode automatically.
    // Otherwise, pick the URL doc, or the first doc, or General if they explicitly clear it.
    useEffect(() => {
        if (documents.isSuccess) {
            if (completedDocs.length === 0) {
                setIsGeneralMode(true);
                setActiveDocId(null);
            } else {
                if (!activeDocId && !isGeneralMode) {
                    setActiveDocId(completedDocs[0].id);
                }
            }
        }
    }, [documents.isSuccess, completedDocs.length, activeDocId, isGeneralMode]);

    const activeDoc = completedDocs.find(d => d.id === activeDocId);

    // --- Council Mode State ---
    const [conversationId, setConversationId] = useState(convIdParam || null);
    const [pendingMessageId, setPendingMessageId] = useState(null);
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [councilWeights, setCouncilWeights] = useState(AGENT_PRESETS.balanced);

    const { mutateAsync: createConv } = useCreateConversation();
    const { data: convData, isLoading: convLoading } = useConversation(conversationId);
    const { mutateAsync: startTurn, isPending: isStarting } = useStartTurn();
    const { mutateAsync: confirmTurn, isPending: isConfirming } = useConfirmTurn();
    const { data: pendingConfig } = useGetConfiguration(conversationId, pendingMessageId);

    // --- General Mode State ---
    const [generalMessages, setGeneralMessages] = useState([]);
    const [generalStream, setGeneralStream] = useState('');
    const [generalStreaming, setGeneralStreaming] = useState(false);
    const [generalError, setGeneralError] = useState(null);

    const messagesEndRef = useRef(null);
    const creatingRef = useRef(false);
    const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });

    useEffect(() => {
        if (activeDocId && !isGeneralMode && !conversationId && !creatingRef.current) {
            creatingRef.current = true;
            createConv(activeDocId).then(data => {
                setConversationId(data.id);
                creatingRef.current = false;
                setSearchParams({ docId: activeDocId, convId: data.id });
            }).catch(err => {
                console.error(err);
                creatingRef.current = false;
            });
        }
    }, [activeDocId, isGeneralMode, conversationId, createConv, setSearchParams]);

    useEffect(() => {
        if (convData?.messages) {
            const pending = convData.messages.find(m => m.status === 'awaiting_confirmation');
            setPendingMessageId(pending ? pending.id : null);
        }
        scrollToBottom();
    }, [convData?.messages, isStarting, pendingMessageId]);

    useEffect(() => {
        scrollToBottom();
    }, [generalMessages, generalStream]);

    const handleSwitchDoc = (docId) => {
        setActiveDocId(docId);
        setIsGeneralMode(docId === null);
        setIsDropdownOpen(false);
        if (docId) {
            setSearchParams({ docId });
            setConversationId(null); // Reset conversation for new doc
        } else {
            setSearchParams({});
        }
    };

    const handleAskQuestion = async (question) => {
        if (isGeneralMode) {
            handleGeneralQuestion(question);
        } else {
            handleCouncilQuestion(question);
        }
    };

    const handleGeneralQuestion = async (question) => {
        setGeneralMessages(prev => [...prev, { role: 'user', content: question }]);
        setGeneralStreaming(true);
        setGeneralStream('');
        setGeneralError(null);

        try {
            const token = useAuthStore.getState().accessToken;
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || '/api/v1'}/conversations/general-stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ question, history: generalMessages })
            });

            if (!response.ok) throw new Error("Failed to connect to general stream");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let accumulated = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split("\n\n");
                
                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        try {
                            const data = JSON.parse(line.substring(6));
                            if (data.type === 'token') {
                                accumulated += data.content;
                                setGeneralStream(accumulated);
                            } else if (data.type === 'error') {
                                setGeneralError(data.message);
                            }
                        } catch (e) {}
                    }
                }
            }
            setGeneralMessages(prev => [...prev, { role: 'assistant', content: accumulated }]);
            setGeneralStream('');
        } catch (err) {
            setGeneralError(err.message);
        } finally {
            setGeneralStreaming(false);
        }
    };

    const handleCouncilQuestion = async (question) => {
        try {
            await startTurn({ conversationId, question, settings: councilWeights });
        } catch (error) {
            console.error(error);
        }
    };

    const handleConfirmConfig = async (config) => {
        try {
            console.log("[ChatPage] confirmTurn entered. payload:", config);
            await confirmTurn({ conversationId, messageId: pendingMessageId, config });
            console.log("[ChatPage] confirmTurn success! resetting pendingMessageId.");
            setPendingMessageId(null);
        } catch (error) {
            console.error("[ChatPage] confirmTurn failed:", error);
        }
    };

    const clearChat = () => {
        if (isGeneralMode) {
            setGeneralMessages([]);
        } else {
            // Ideally we'd hit an API to clear the DB conversation, but for now we reset ID
            setConversationId(null);
            if (activeDocId) createConv(activeDocId).then(data => setConversationId(data.id));
        }
    };

    return (
        <div className="flex flex-col h-full bg-white dark:bg-slate-950 relative overflow-hidden">
            {/* Header / Document Context Bar */}
            <div className="flex items-center justify-between shrink-0 h-16 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-4 sm:px-6 lg:px-8 relative z-30">
                <div className="relative">
                    <button 
                        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                        className="flex items-center gap-3 hover:bg-slate-50 dark:hover:bg-slate-900 p-2 rounded-md transition-colors text-left"
                    >
                        <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${isGeneralMode ? 'bg-emerald-100 text-emerald-600' : 'bg-indigo-100 text-indigo-600'}`}>
                            {isGeneralMode ? <MessageSquare className="h-5 w-5" /> : <FileText className="h-5 w-5" />}
                        </div>
                        <div>
                            <div className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                                {isGeneralMode ? 'General Chat' : activeDoc?.filename || 'No document selected'}
                                <ChevronDown className="h-4 w-4 text-slate-400" />
                            </div>
                            <div className="text-xs text-slate-500 flex items-center gap-1">
                                {isGeneralMode ? 'No Document Context' : (
                                    <>
                                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
                                        Indexed Document (Research Mode)
                                    </>
                                )}
                            </div>
                        </div>
                    </button>
                    
                    {isDropdownOpen && (
                        <div className="absolute top-full left-0 mt-2 w-72 bg-white dark:bg-slate-900 rounded-xl shadow-xl border border-slate-200 dark:border-slate-800 py-2">
                            <div className="px-3 pb-2 mb-2 border-b border-slate-100 dark:border-slate-800">
                                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Chat Modes</p>
                            </div>
                            <button 
                                onClick={() => handleSwitchDoc(null)}
                                className={`w-full flex items-center gap-3 px-4 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors ${isGeneralMode ? 'bg-slate-50 dark:bg-slate-800' : ''}`}
                            >
                                <MessageSquare className="h-4 w-4 text-emerald-500" />
                                <span className="flex-1 text-left text-slate-700 dark:text-slate-300">General Chat</span>
                                {isGeneralMode && <Check className="h-4 w-4 text-indigo-600" />}
                            </button>
                            
                            <div className="px-3 py-2 mt-2 mb-2 border-y border-slate-100 dark:border-slate-800">
                                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Indexed Documents</p>
                            </div>
                            {completedDocs.length === 0 ? (
                                <p className="px-4 py-2 text-xs text-slate-500 italic">No indexed documents available.</p>
                            ) : (
                                <div className="max-h-60 overflow-y-auto">
                                    {completedDocs.map(doc => (
                                        <button 
                                            key={doc.id}
                                            onClick={() => handleSwitchDoc(doc.id)}
                                            className={`w-full flex items-center gap-3 px-4 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors ${activeDocId === doc.id ? 'bg-slate-50 dark:bg-slate-800' : ''}`}
                                        >
                                            <FileText className="h-4 w-4 text-indigo-500" />
                                            <span className="flex-1 text-left truncate text-slate-700 dark:text-slate-300">{doc.filename}</span>
                                            {activeDocId === doc.id && <Check className="h-4 w-4 text-indigo-600" />}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>

                <div className="flex items-center gap-2">
                    <button onClick={clearChat} className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors" title="Clear Chat">
                        <Trash2 className="w-5 h-5" />
                    </button>
                    {!isGeneralMode && (
                        <button 
                            onClick={() => setIsSettingsOpen(!isSettingsOpen)} 
                            className={`p-2 rounded-md transition-colors ${isSettingsOpen ? 'bg-slate-200 text-slate-900 dark:bg-slate-800 dark:text-white' : 'text-slate-500 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800'}`}
                            title="Agent Configuration"
                        >
                            <Settings className="w-5 h-5" />
                        </button>
                    )}
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="flex-1 overflow-y-auto pb-32">
                {!isGeneralMode && (!conversationId || convLoading) ? (
                    <div className="flex flex-col items-center justify-center h-full text-slate-500">
                        <Loader2 className="w-8 h-8 animate-spin text-indigo-600 mb-4" />
                        <p>Initializing AI Council for {activeDoc?.filename}...</p>
                    </div>
                ) : (isGeneralMode ? generalMessages : convData?.messages || []).length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center px-4 animate-in fade-in slide-in-from-bottom-4">
                        <div className={`p-5 rounded-full mb-6 ${isGeneralMode ? 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600' : 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600'}`}>
                            {isGeneralMode ? <MessageSquare className="w-12 h-12" /> : <Bot className="w-12 h-12" />}
                        </div>
                        <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
                            {isGeneralMode ? 'General AI Assistant' : 'AI Council Research Mode'}
                        </h3>
                        <p className="text-slate-500 max-w-md">
                            {isGeneralMode 
                                ? "Ask me anything. I can assist with general knowledge, coding, or text processing." 
                                : `The AI Council is ready to analyze "${activeDoc?.filename}". Ask a question to trigger the agents.`}
                        </p>
                    </div>
                ) : (
                    <div className="divide-y divide-slate-100 dark:divide-slate-800/50">
                        {isGeneralMode ? (
                            generalMessages.map((msg, idx) => (
                                <ChatMessage key={idx} role={msg.role} content={msg.content} isGeneral={true} />
                            ))
                        ) : (
                            convData.messages?.map((msg, idx) => (
                                <ConversationMessage 
                                    key={msg.id} 
                                    message={msg} 
                                    conversationId={conversationId} 
                                    isLatest={idx === convData.messages.length - 1} 
                                />
                            ))
                        )}
                        
                        {generalStreaming && (
                            <ChatMessage role="assistant" content={generalStream} isStreaming={true} isGeneral={true} />
                        )}
                        
                        {!isGeneralMode && isStarting && (
                            <div className="flex w-full py-8 px-4 md:px-6 lg:px-8 bg-slate-50 dark:bg-slate-900/50">
                                <div className="max-w-4xl mx-auto w-full flex gap-4 md:gap-6">
                                    <div className="shrink-0 flex h-8 w-8 items-center justify-center rounded-sm bg-indigo-600 text-white shadow-sm">
                                        <Loader2 className="h-5 w-5 animate-spin" />
                                    </div>
                                    <div className="flex-1 min-w-0 pt-1 text-slate-500 italic">
                                        Preparing the AI Council...
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            {/* Input & Settings */}
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-white via-white to-transparent dark:from-slate-950 dark:via-slate-950 pt-10 pb-6 px-4 sm:px-6 lg:px-8 z-20">
                <div className="max-w-4xl mx-auto flex flex-col gap-4">
                    {generalError && (
                        <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm border border-red-100 shadow-sm animate-in fade-in">
                            {generalError}
                        </div>
                    )}
                    
                    {!isGeneralMode && pendingConfig && (
                        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl shadow-lg overflow-hidden animate-in slide-in-from-bottom-4">
                            <CouncilWeightPanel 
                                configuration={pendingConfig} 
                                onConfirm={handleConfirmConfig} 
                                isConfirming={isConfirming} 
                            />
                        </div>
                    )}

                    <div className="shadow-lg shadow-slate-200/50 dark:shadow-none rounded-xl">
                        <QuestionInput 
                            onSubmit={handleAskQuestion} 
                            isLoading={generalStreaming || isStarting || !!pendingMessageId || isConfirming} 
                            placeholder={isGeneralMode ? "Message General AI..." : "Ask the AI Council..."}
                        />
                    </div>
                </div>
            </div>
            
            {/* Agent Weight Config Drawer */}
            <div className={`absolute top-16 right-0 bottom-0 w-80 bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 shadow-2xl z-40 transition-transform transform duration-300 ease-in-out ${isSettingsOpen && !isGeneralMode ? 'translate-x-0' : 'translate-x-full'}`}>
                <div className="p-6 h-full flex flex-col overflow-y-auto">
                    <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
                        <Settings className="h-5 w-5 text-indigo-500" />
                        Agent Weights
                    </h3>
                    
                    <div className="space-y-6">
                        <div>
                            <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-3">Presets</label>
                            <div className="grid grid-cols-2 gap-2">
                                {Object.keys(AGENT_PRESETS).map(preset => (
                                    <button
                                        key={preset}
                                        onClick={() => setCouncilWeights(AGENT_PRESETS[preset])}
                                        className="px-3 py-2 text-xs font-medium rounded-md border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-colors capitalize"
                                    >
                                        {preset.replace('_', ' ')}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="space-y-5 border-t border-slate-100 dark:border-slate-800 pt-5">
                            {Object.entries(councilWeights).map(([agent, weight]) => (
                                <div key={agent}>
                                    <div className="flex justify-between items-center mb-2 text-sm">
                                        <span className="font-medium text-slate-700 dark:text-slate-300 capitalize">{agent}</span>
                                        <span className="text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded text-xs">{weight}%</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="0"
                                        max="100"
                                        value={weight}
                                        onChange={(e) => setCouncilWeights(prev => ({ ...prev, [agent]: parseInt(e.target.value) }))}
                                        className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                                    />
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function ChatMessage({ role, content, isStreaming, isGeneral }) {
    const isUser = role === 'user';
    return (
        <div className={`flex w-full py-8 px-4 md:px-6 lg:px-8 ${isUser ? 'bg-white dark:bg-slate-950' : 'bg-slate-50 dark:bg-slate-900/50'} group`}>
            <div className="max-w-4xl mx-auto w-full flex gap-4 md:gap-6 relative">
                <div className="shrink-0 flex flex-col items-center">
                    <div className={`flex h-8 w-8 items-center justify-center rounded-sm shadow-sm ${
                        isUser ? 'bg-emerald-500 text-white' : 'bg-indigo-600 text-white'
                    }`}>
                        {isUser ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
                    </div>
                </div>
                <div className="flex-1 min-w-0 pt-1">
                    <span className="font-semibold text-slate-900 dark:text-white block mb-2">
                        {isUser ? 'You' : isGeneral ? 'General Assistant' : 'Council of Minds'}
                    </span>
                    <div className="prose prose-slate dark:prose-invert max-w-none text-slate-700 dark:text-slate-300 text-[15px] leading-relaxed">
                        {isUser ? (
                            <div className="whitespace-pre-wrap">{content}</div>
                        ) : (
                            <>
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
                                {isStreaming && <span className="inline-block w-2 h-4 ml-1 bg-indigo-600 animate-pulse"></span>}
                            </>
                        )}
                    </div>
                </div>
                {!isUser && content && !isStreaming && (
                    <button 
                        onClick={() => navigator.clipboard.writeText(content)}
                        className="absolute top-0 right-0 p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity rounded-md hover:bg-slate-200 dark:hover:bg-slate-700"
                        title="Copy to clipboard"
                    >
                        <Copy className="h-4 w-4" />
                    </button>
                )}
            </div>
        </div>
    );
}
