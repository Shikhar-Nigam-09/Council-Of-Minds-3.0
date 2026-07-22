import React from 'react';

const ComparisonPanel = ({ run }) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded shadow p-4 border-t-4 border-gray-400">
                <div className="flex justify-between items-center border-b pb-2 mb-4">
                    <h3 className="font-bold text-lg">Single Agent</h3>
                    <div className="text-xs text-right">
                        <p className="text-gray-500">{run.single_agent_latency_ms} ms</p>
                        <p className="text-gray-500">${Number(run.single_agent_cost_estimate).toFixed(4)}</p>
                    </div>
                </div>
                <div className="prose prose-sm max-w-none whitespace-pre-wrap">
                    {run.single_agent_answer || "No answer generated."}
                </div>
            </div>

            <div className="bg-white rounded shadow p-4 border-t-4 border-indigo-500">
                <div className="flex justify-between items-center border-b pb-2 mb-4">
                    <h3 className="font-bold text-lg text-indigo-700">Council of Minds</h3>
                    <div className="text-xs text-right">
                        <p className="text-gray-500">{run.council_latency_ms} ms</p>
                        <p className="text-gray-500">${Number(run.council_cost_estimate).toFixed(4)}</p>
                    </div>
                </div>
                <div className="prose prose-sm max-w-none whitespace-pre-wrap">
                    {run.council_answer || "No answer generated."}
                </div>
            </div>
        </div>
    );
};

export default ComparisonPanel;
