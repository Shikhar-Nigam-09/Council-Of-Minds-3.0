import React from 'react';
import { useAuthStore } from '../../store/authStore';
import { useDocuments } from '../../features/documents/useDocuments';
import { Files, MessageSquare, Activity, ChevronRight, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function DashboardPage() {
    const user = useAuthStore(state => state.user);
    const { documents } = useDocuments();
    
    const docs = documents.data?.data || [];
    const totalDocs = docs.length;
    const completedDocs = docs.filter(d => d.status === 'completed').length;
    const processingDocs = docs.filter(d => d.status === 'processing' || d.status === 'queued').length;
    const recentDocs = [...docs].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 3);
    
    const [totalConvs, setTotalConvs] = React.useState(0);
    React.useEffect(() => {
        import('../../lib/axios').then(({ default: api }) => {
            api.get('/conversations').then(res => {
                setTotalConvs(res.data.length);
            }).catch(() => {});
        });
    }, []);

    const metrics = [
        { name: 'Total Documents', value: totalDocs, icon: Files, color: 'text-indigo-600', bg: 'bg-indigo-100' },
        { name: 'Processed & Ready', value: completedDocs, icon: Activity, color: 'text-emerald-600', bg: 'bg-emerald-100' },
        { name: 'Active Conversations', value: totalConvs, icon: MessageSquare, color: 'text-purple-600', bg: 'bg-purple-100' },
    ];

    return (
        <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Dashboard</h2>
                    <p className="text-sm text-slate-500 mt-1">
                        Welcome back, {user?.full_name?.split(' ')[0] || 'User'}. Here's what's happening today.
                    </p>
                </div>
                <Link
                    to="/documents"
                    className="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition-colors"
                >
                    Upload Document
                </Link>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {metrics.map((metric) => (
                    <div
                        key={metric.name}
                        className="relative overflow-hidden rounded-xl bg-white px-6 py-6 shadow-sm ring-1 ring-slate-200 transition-all hover:shadow-md dark:bg-slate-900 dark:ring-slate-800"
                    >
                        <dt>
                            <div className={`absolute rounded-xl p-3 ${metric.bg}`}>
                                <metric.icon className={`h-6 w-6 ${metric.color}`} aria-hidden="true" />
                            </div>
                            <p className="ml-16 truncate text-sm font-medium text-slate-500">{metric.name}</p>
                        </dt>
                        <dd className="ml-16 flex items-baseline pb-1">
                            <p className="text-2xl font-semibold text-slate-900 dark:text-white">{metric.value}</p>
                        </dd>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Recent Documents */}
                <div className="rounded-xl bg-white shadow-sm ring-1 ring-slate-200 dark:bg-slate-900 dark:ring-slate-800 overflow-hidden">
                    <div className="border-b border-slate-200 dark:border-slate-800 px-6 py-5">
                        <h3 className="text-base font-semibold leading-6 text-slate-900 dark:text-white">Recent Documents</h3>
                    </div>
                    <ul role="list" className="divide-y divide-slate-200 dark:divide-slate-800">
                        {documents.isLoading ? (
                            <div className="p-6 text-center text-sm text-slate-500 animate-pulse">Loading documents...</div>
                        ) : recentDocs.length > 0 ? (
                            recentDocs.map((doc) => (
                                <li key={doc.id} className="relative flex justify-between gap-x-6 px-6 py-5 hover:bg-slate-50 transition-colors dark:hover:bg-slate-800/50">
                                    <div className="flex min-w-0 gap-x-4">
                                        <div className="flex h-12 w-12 flex-none items-center justify-center rounded-lg bg-slate-100 ring-1 ring-slate-200 dark:bg-slate-800 dark:ring-slate-700">
                                            <Files className="h-6 w-6 text-slate-500" aria-hidden="true" />
                                        </div>
                                        <div className="min-w-0 flex-auto">
                                            <p className="text-sm font-semibold leading-6 text-slate-900 dark:text-white">
                                                <Link to={`/documents/${doc.id}`} className="hover:underline">
                                                    <span className="absolute inset-x-0 -top-px bottom-0" />
                                                    {doc.filename}
                                                </Link>
                                            </p>
                                            <p className="mt-1 flex text-xs leading-5 text-slate-500">
                                                {new Date(doc.created_at).toLocaleDateString()}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex shrink-0 items-center gap-x-4">
                                        <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                                            doc.status === 'completed' ? 'bg-emerald-50 text-emerald-700 ring-emerald-600/20' :
                                            doc.status === 'failed' ? 'bg-red-50 text-red-700 ring-red-600/20' :
                                            'bg-amber-50 text-amber-700 ring-amber-600/20'
                                        }`}>
                                            {doc.status}
                                        </span>
                                        <ChevronRight className="h-5 w-5 flex-none text-slate-400" aria-hidden="true" />
                                    </div>
                                </li>
                            ))
                        ) : (
                            <li className="px-6 py-8 text-center text-sm text-slate-500">
                                No documents uploaded yet.
                            </li>
                        )}
                    </ul>
                    {totalDocs > 3 && (
                        <div className="border-t border-slate-200 dark:border-slate-800 px-6 py-4">
                            <Link to="/documents" className="text-sm font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
                                View all documents <span aria-hidden="true">&rarr;</span>
                            </Link>
                        </div>
                    )}
                </div>
                
                {/* AI Workflows Teaser / Quick Start */}
                <div className="rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-sm overflow-hidden text-white relative">
                    <div className="absolute -right-20 -top-20 opacity-10">
                        <MessageSquare className="h-64 w-64" />
                    </div>
                    <div className="px-8 py-10 relative z-10 h-full flex flex-col justify-center">
                        <h3 className="text-2xl font-bold mb-4">Start an AI Council</h3>
                        <p className="text-indigo-100 mb-8 max-w-sm">
                            Analyze your documents with a panel of specialized AI agents. Discuss, debate, and extract insights from your data.
                        </p>
                        <div>
                            <Link
                                to="/chat"
                                className="inline-flex items-center rounded-lg bg-white px-5 py-2.5 text-sm font-semibold text-indigo-600 shadow-sm hover:bg-indigo-50 transition-colors"
                            >
                                Select a document to chat
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
