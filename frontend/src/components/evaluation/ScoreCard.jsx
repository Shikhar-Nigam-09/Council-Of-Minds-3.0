import React from 'react';

const ScoreCard = ({ verdict, status }) => {
    if (status !== 'success' || !verdict) {
        return (
            <div className="bg-yellow-50 p-4 rounded border border-yellow-200 mb-6">
                <p className="text-yellow-700">Judge failed to produce a valid score for this run.</p>
            </div>
        );
    }

    const { single_agent, council, comparative_verdict } = verdict;

    const renderScores = (title, data) => (
        <div className="bg-white p-4 rounded shadow border">
            <h3 className="font-bold text-lg border-b pb-2 mb-2">{title}</h3>
            <div className="grid grid-cols-3 gap-2 text-center mb-4">
                <div className="bg-gray-50 p-2 rounded">
                    <div className="text-sm text-gray-500">Quality</div>
                    <div className="text-xl font-semibold">{data.quality_score}/10</div>
                </div>
                <div className="bg-gray-50 p-2 rounded">
                    <div className="text-sm text-gray-500">Completeness</div>
                    <div className="text-xl font-semibold">{data.completeness_score}/10</div>
                </div>
                <div className="bg-gray-50 p-2 rounded">
                    <div className="text-sm text-gray-500">Citations</div>
                    <div className="text-xl font-semibold">{data.citation_quality_score}/10</div>
                </div>
            </div>
            <p className="text-sm text-gray-700 italic">"{data.reasoning}"</p>
        </div>
    );

    return (
        <div className="mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                {renderScores("Single Agent Baseline", single_agent)}
                {renderScores("Council Pipeline", council)}
            </div>
            <div className="bg-indigo-50 p-4 rounded border border-indigo-100">
                <h3 className="font-bold text-indigo-900 mb-1">Judge Verdict</h3>
                <p className="text-indigo-800">{comparative_verdict}</p>
            </div>
        </div>
    );
};

export default ScoreCard;
