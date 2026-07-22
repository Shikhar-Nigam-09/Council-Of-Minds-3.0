import React, { useState } from 'react';
import { useEvaluationRuns, useRunEvaluation } from '../../features/evaluation/useEvaluation';
import { useDocuments } from '../../features/documents/useDocuments';
import EvaluationHistoryTable from '../../components/evaluation/EvaluationHistoryTable';
import ComparisonPanel from '../../components/evaluation/ComparisonPanel';
import ScoreCard from '../../components/evaluation/ScoreCard';

const EvaluationPage = () => {
    const [selectedDoc, setSelectedDoc] = useState('');
    const [question, setQuestion] = useState('');
    const [activeRun, setActiveRun] = useState(null);
    
    const { data: documents } = useDocuments();
    const { data: runs, isLoading: isRunsLoading } = useEvaluationRuns();
    const runEvalMutation = useRunEvaluation();

    const handleRun = async (e) => {
        e.preventDefault();
        if (!selectedDoc || !question) return;
        
        try {
            const result = await runEvalMutation.mutateAsync({ 
                documentId: selectedDoc, 
                question 
            });
            setActiveRun(result);
        } catch (err) {
            console.error("Evaluation failed", err);
        }
    };

    return (
        <div className="container mx-auto p-6 max-w-6xl">
            <h1 className="text-3xl font-bold mb-6">Internal Evaluation Tool</h1>
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
                <p className="text-red-700 font-bold">INTERNAL USE ONLY</p>
                <p className="text-sm text-red-600">This page runs cost-intensive benchmarking pipelines. LLM Judge signals are rough indicators, not rigorous benchmarks.</p>
            </div>

            <div className="bg-white rounded shadow p-6 mb-8">
                <h2 className="text-xl font-semibold mb-4">Run New Evaluation</h2>
                <form onSubmit={handleRun} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Select Document</label>
                        <select 
                            className="w-full border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border"
                            value={selectedDoc}
                            onChange={(e) => setSelectedDoc(e.target.value)}
                            required
                        >
                            <option value="">-- Select a document --</option>
                            {documents?.map(doc => (
                                <option key={doc.id} value={doc.id}>{doc.filename}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Test Question</label>
                        <input 
                            type="text" 
                            className="w-full border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border"
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            placeholder="Enter a complex question to benchmark..."
                            required
                        />
                    </div>
                    <button 
                        type="submit" 
                        disabled={runEvalMutation.isPending}
                        className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50"
                    >
                        {runEvalMutation.isPending ? 'Running Pipeline...' : 'Run Evaluation'}
                    </button>
                </form>
            </div>

            {activeRun && (
                <div className="mb-12">
                    <h2 className="text-2xl font-bold mb-4">Latest Result</h2>
                    <ScoreCard verdict={activeRun.judge_verdict} status={activeRun.judge_status} />
                    <ComparisonPanel run={activeRun} />
                </div>
            )}

            <div className="bg-white rounded shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Evaluation History</h2>
                {isRunsLoading ? (
                    <p>Loading history...</p>
                ) : (
                    <EvaluationHistoryTable runs={runs} onSelectRun={setActiveRun} />
                )}
            </div>
        </div>
    );
};

export default EvaluationPage;
