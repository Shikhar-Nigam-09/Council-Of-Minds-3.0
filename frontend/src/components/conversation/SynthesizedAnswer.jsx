import React from 'react';
import { CitationChip } from './CitationChip';

export const SynthesizedAnswer = ({ text }) => {
    if (!text) return null;
    
    const parts = text.split(/(\[[a-fA-F0-9-]{36}\]|\[[a-zA-Z0-9-]+\])/g);
    
    return (
        <div className="prose dark:prose-invert max-w-none text-sm leading-relaxed">
            {parts.map((part, i) => {
                if (part.startsWith('[') && part.endsWith(']')) {
                    const chunkId = part.slice(1, -1);
                    return <CitationChip key={i} chunkId={chunkId} onClick={() => console.log('Chunk clicked', chunkId)} />;
                }
                return <span key={i}>{part}</span>;
            })}
        </div>
    );
};
