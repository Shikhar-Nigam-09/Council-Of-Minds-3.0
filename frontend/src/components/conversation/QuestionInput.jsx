import React, { useState, useRef, useEffect } from 'react';
import { SendHorizontal, Loader2 } from 'lucide-react';

export const QuestionInput = ({ onSubmit, isLoading }) => {
    const [question, setQuestion] = useState('');
    const textareaRef = useRef(null);

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'inherit';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
        }
    }, [question]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (question.trim() && !isLoading) {
            onSubmit(question);
            setQuestion('');
            if (textareaRef.current) {
                textareaRef.current.style.height = 'inherit';
            }
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="relative max-w-4xl mx-auto w-full">
            <div className="relative flex items-end w-full overflow-hidden rounded-2xl bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 shadow-sm focus-within:ring-2 focus-within:ring-indigo-600 focus-within:border-transparent transition-all">
                <textarea
                    ref={textareaRef}
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask a question about this document..."
                    className="flex-1 max-h-[200px] min-h-[56px] w-full resize-none bg-transparent px-4 py-4 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none sm:text-sm sm:leading-6"
                    disabled={isLoading}
                    rows={1}
                />
                <div className="flex shrink-0 p-2">
                    <button
                        type="submit"
                        disabled={!question.trim() || isLoading}
                        className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white transition-colors hover:bg-indigo-500 disabled:bg-slate-100 disabled:text-slate-400 dark:disabled:bg-slate-800 dark:disabled:text-slate-500"
                    >
                        {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <SendHorizontal className="h-5 w-5" />}
                    </button>
                </div>
            </div>
            <div className="mt-2 text-center text-xs text-slate-500">
                Council of Minds can make mistakes. Consider verifying important information.
            </div>
        </form>
    );
};
