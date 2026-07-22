import React from 'react';

export const CitationChip = ({ chunkId, onClick }) => {
    return (
        <button 
            onClick={() => onClick && onClick(chunkId)}
            className="inline-flex items-center justify-center px-1.5 py-0.5 mx-1 text-xs font-mono bg-blue-100 text-blue-800 rounded hover:bg-blue-200 transition-colors"
            title={`View source chunk ${chunkId}`}
        >
            [{chunkId.substring(0, 8)}]
        </button>
    );
};
