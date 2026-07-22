import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { useDocuments } from '../../features/documents/useDocuments';
import { StatusBadge } from '../../components/documents/StatusBadge';
import { ProcessingReport } from '../../components/documents/ProcessingReport';
import { ArrowLeft, FileText, Database } from 'lucide-react';

export default function DocumentDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { useDocumentDetail } = useDocuments();
    const { data: documentData, isLoading } = useDocumentDetail(id);
    
    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    if (!documentData) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
                <h2 className="text-xl font-semibold text-gray-900">Document not found</h2>
                <button onClick={() => navigate('/documents')} className="mt-4 text-indigo-600 hover:underline">
                    Back to documents
                </button>
            </div>
        );
    }
    
    const doc = documentData.data.document;
    const chunks = documentData.data.chunks || [];
    
    const chunkCounts = chunks.reduce((acc, chunk) => {
        acc[chunk.chunk_type] = (acc[chunk.chunk_type] || 0) + 1;
        return acc;
    }, {});

    return (
        <div className="min-h-screen bg-gray-50 pb-12">
            <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
                <button 
                    onClick={() => navigate('/documents')}
                    className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-6 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Back to Documents
                </button>

                <div className="bg-white p-6 rounded-xl shadow-sm border mb-8">
                    <div className="flex items-start justify-between">
                        <div className="flex items-center gap-4">
                            <div className="p-4 bg-indigo-50 text-indigo-600 rounded-xl">
                                <FileText className="w-8 h-8" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">{doc.filename}</h1>
                                <div className="flex items-center gap-4 text-sm text-gray-500 mt-2 mb-4">
                                    <span>{(doc.file_size_bytes / (1024 * 1024)).toFixed(2)} MB</span>
                                    <span>•</span>
                                    <span>{format(new Date(doc.created_at), 'MMM d, yyyy h:mm a')}</span>
                                    <span>•</span>
                                    <span>{doc.page_count ? `${doc.page_count} Pages` : 'Calculating pages...'}</span>
                                </div>
                                <button 
                                    onClick={() => navigate(`/chat?docId=${id}`)}
                                    disabled={doc.status !== 'completed'}
                                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors disabled:opacity-50"
                                >
                                    Start Conversation
                                </button>
                            </div>
                        </div>
                        <StatusBadge status={doc.status} />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="bg-white p-6 rounded-xl shadow-sm border">
                        <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
                            <Database className="w-5 h-5 text-indigo-600" />
                            Chunk Statistics
                        </h3>
                        {chunks.length > 0 ? (
                            <div className="space-y-3">
                                {Object.entries(chunkCounts).map(([type, count]) => (
                                    <div key={type} className="flex justify-between items-center py-2 border-b last:border-0">
                                        <span className="capitalize text-gray-700">{type.replace('_', ' ')}</span>
                                        <span className="font-semibold text-indigo-600 bg-indigo-50 px-2 py-1 rounded-md text-sm">
                                            {count} chunks
                                        </span>
                                    </div>
                                ))}
                                <div className="flex justify-between items-center pt-2 mt-2">
                                    <span className="font-medium text-gray-900">Total Chunks</span>
                                    <span className="font-bold text-gray-900">{chunks.length}</span>
                                </div>
                            </div>
                        ) : (
                            <div className="text-sm text-gray-500 py-4 text-center bg-gray-50 rounded-lg">
                                No chunks extracted yet.
                            </div>
                        )}
                    </div>

                    <div className="bg-white p-6 rounded-xl shadow-sm border">
                        <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
                            <FileText className="w-5 h-5 text-indigo-600" />
                            Processing Report
                        </h3>
                        <ProcessingReport report={doc.processing_report} />
                    </div>
                </div>
            </div>
        </div>
    );
}
