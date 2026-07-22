import React from 'react';

export const CouncilProgress = ({ statuses }) => {
    const agents = ['logical', 'practical', 'analytical', 'skeptical', 'ethics'];
    
    const getStatusStyle = (status) => {
        switch(status) {
            case 'pending': return 'bg-gray-200 text-gray-500';
            case 'running': return 'bg-blue-100 text-blue-700 animate-pulse';
            case 'complete': return 'bg-green-100 text-green-700';
            case 'failed': return 'bg-red-100 text-red-700';
            default: return 'bg-gray-100 text-gray-500';
        }
    };

    return (
        <div className="flex flex-wrap gap-2 mb-4">
            {agents.map(agent => (
                <div 
                    key={agent} 
                    className={`px-3 py-1.5 rounded-full text-xs font-medium flex items-center space-x-1 capitalize transition-colors ${getStatusStyle(statuses[agent] || 'pending')}`}
                >
                    {statuses[agent] === 'running' && (
                        <span className="w-2 h-2 rounded-full bg-blue-500 mr-1 animate-ping"></span>
                    )}
                    <span>{agent}</span>
                </div>
            ))}
        </div>
    );
};
