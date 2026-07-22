import React, { useState, useMemo } from 'react';
import { UploadDropzone } from '../../features/documents/UploadDropzone';
import { DocumentCard } from '../../components/documents/DocumentCard';
import { useDocuments } from '../../features/documents/useDocuments';
import { FileStack, Search, Filter } from 'lucide-react';
import { toast } from 'sonner';

export default function DocumentsPage() {
    const { documents, upload, deleteDocument } = useDocuments();
    const [uploadProgress, setUploadProgress] = useState(0);
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');

    const handleUpload = (file) => {
        upload.mutate({
            file,
            onUploadProgress: (progressEvent) => {
                const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                setUploadProgress(percentCompleted);
            }
        }, {
            onSuccess: () => toast.success("Document uploaded successfully"),
            onSettled: () => setUploadProgress(0),
            onError: (error) => {
                toast.error(error.response?.data?.error?.message || "Upload failed");
            }
        });
    };

    const handleDelete = (id) => {
        deleteDocument.mutate(id, {
            onSuccess: () => toast.success("Document deleted"),
            onError: (error) => {
                toast.error(error.response?.data?.error?.message || "Delete failed");
            }
        });
    };

    const docs = documents.data?.data || [];
    
    const filteredDocs = useMemo(() => {
        return docs.filter(doc => {
            const matchesSearch = doc.filename.toLowerCase().includes(searchQuery.toLowerCase());
            const matchesFilter = statusFilter === 'all' || doc.status === statusFilter;
            return matchesSearch && matchesFilter;
        });
    }, [docs, searchQuery, statusFilter]);

    return (
        <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Documents</h2>
                    <p className="text-sm text-slate-500 mt-1">Upload and manage your PDF documents for AI analysis.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Upload */}
                <div className="lg:col-span-1">
                    <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 sticky top-8">
                        <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-4">Upload New</h3>
                        <UploadDropzone 
                            onUpload={handleUpload} 
                            isUploading={upload.isPending} 
                            progress={uploadProgress} 
                        />
                    </div>
                </div>

                {/* Right Column: Document List */}
                <div className="lg:col-span-2 flex flex-col gap-6">
                    {/* Controls */}
                    <div className="flex flex-col sm:flex-row gap-4">
                        <div className="relative flex-1">
                            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                                <Search className="h-5 w-5 text-slate-400" aria-hidden="true" />
                            </div>
                            <input
                                type="text"
                                className="block w-full rounded-lg border-0 py-2.5 pl-10 text-slate-900 ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 dark:bg-slate-900 dark:text-white dark:ring-slate-700"
                                placeholder="Search documents..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>
                        <div className="relative shrink-0">
                            <select
                                className="block w-full rounded-lg border-0 py-2.5 pl-3 pr-10 text-slate-900 ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6 dark:bg-slate-900 dark:text-white dark:ring-slate-700"
                                value={statusFilter}
                                onChange={(e) => setStatusFilter(e.target.value)}
                            >
                                <option value="all">All Statuses</option>
                                <option value="completed">Completed</option>
                                <option value="processing">Processing</option>
                                <option value="queued">Queued</option>
                                <option value="failed">Failed</option>
                            </select>
                        </div>
                    </div>

                    {/* List */}
                    <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden min-h-[400px]">
                        <div className="flex justify-between items-center px-6 py-4 border-b border-slate-200 dark:border-slate-800">
                            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Your Files</h3>
                            {docs.length > 0 && (
                                <span className="text-xs font-medium text-slate-500 bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded-full">
                                    {filteredDocs.length} of {docs.length}
                                </span>
                            )}
                        </div>

                        {documents.isLoading ? (
                            <div className="flex flex-col justify-center items-center h-64 space-y-4">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                                <p className="text-sm text-slate-500">Loading documents...</p>
                            </div>
                        ) : filteredDocs.length > 0 ? (
                            <div className="p-4 space-y-3">
                                {filteredDocs.map(doc => (
                                    <DocumentCard 
                                        key={doc.id} 
                                        document={doc} 
                                        onDelete={handleDelete}
                                        isDeleting={deleteDocument.isPending && deleteDocument.variables === doc.id}
                                    />
                                ))}
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center h-64 text-center px-4">
                                <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-full mb-4">
                                    <FileStack className="w-10 h-10 text-slate-400" />
                                </div>
                                <h3 className="text-base font-semibold text-slate-900 dark:text-white">No documents found</h3>
                                <p className="text-sm text-slate-500 mt-1 max-w-sm">
                                    {searchQuery || statusFilter !== 'all' 
                                        ? "Try adjusting your search or filters to find what you're looking for." 
                                        : "Get started by uploading a PDF document. Your files will appear here once processed."}
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
