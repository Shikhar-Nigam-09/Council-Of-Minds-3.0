import React, { useState } from 'react';

export const AgentOutputPanel = ({ agentName, output }) => {
    const [expanded, setExpanded] = useState(false);

    if (!output) return null;

    const statusColors = {
        success: 'text-green-600',
        failed: 'text-red-600'
    };

    return (
        <div className="border rounded-lg mb-2 overflow-hidden bg-white dark:bg-gray-800">
            <button 
                onClick={() => setExpanded(!expanded)}
                className="w-full px-4 py-3 flex justify-between items-center bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            >
                <div className="flex items-center space-x-2">
                    <span className="font-semibold capitalize">{agentName}</span>
                    <span className={`text-sm ${statusColors[output.status] || 'text-gray-500'}`}>
                        ({output.status})
                    </span>
                    {output.included_in_synthesis && (
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full ml-2">
                            Weight: {output.weight_used}%
                        </span>
                    )}
                </div>
                <span>{expanded ? '▲' : '▼'}</span>
            </button>
            
            {expanded && (
                <div className="p-4 border-t">
                    {output.status === 'failed' ? (
                        <div className="text-red-600">
                            Failed: {output.error_message || 'Unknown error'}
                        </div>
                    ) : (
                        <div>
                            <h4 className="font-semibold mb-2 text-sm text-gray-500 uppercase">Summary</h4>
                            <p className="mb-4 text-sm">{output.summary}</p>
                            
                            {output.evidence_points && output.evidence_points.length > 0 && (
                                <>
                                    <h4 className="font-semibold mb-2 text-sm text-gray-500 uppercase">Evidence Points</h4>
                                    <ul className="space-y-3">
                                        {output.evidence_points.map((ep, i) => (
                                            <li key={i} className="text-sm bg-gray-50 dark:bg-gray-700 p-3 rounded">
                                                <div className="mb-1">{ep.claim}</div>
                                                <div className="flex items-center justify-between mt-2">
                                                    <span className="text-xs text-gray-500 font-mono">
                                                        Source: {ep.supporting_chunk_id}
                                                    </span>
                                                    <span className={`text-xs px-2 py-0.5 rounded ${
                                                        ep.confidence === 'high' ? 'bg-green-100 text-green-800' :
                                                        ep.confidence === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                                        'bg-red-100 text-red-800'
                                                    }`}>
                                                        {ep.confidence}
                                                    </span>
                                                </div>
                                            </li>
                                        ))}
                                    </ul>
                                </>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
