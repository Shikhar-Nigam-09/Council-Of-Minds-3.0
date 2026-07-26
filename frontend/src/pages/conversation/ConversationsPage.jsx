import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { MessageSquare, Trash2, Calendar, FileText } from 'lucide-react';
import { toast } from 'sonner';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import api from '../../lib/axios';

export default function ConversationsPage() {
    const [conversations, setConversations] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isDeleting, setIsDeleting] = useState(false);

    useEffect(() => {
        fetchConversations();
    }, []);

    const fetchConversations = async () => {
        try {
            const res = await api.get('/api/v1/conversations');
            setConversations(res.data);
        } catch (error) {
            toast.error("Failed to load conversations");
        } finally {
            setIsLoading(false);
        }
    };

    const handleDelete = async (id) => {
        setIsDeleting(true);
        try {
            await api.delete(`/api/v1/conversations/${id}`);
            toast.success("Conversation deleted");
            setConversations(conversations.filter(c => c.id !== id));
        } catch (error) {
            toast.error("Failed to delete conversation");
        } finally {
            setIsDeleting(false);
        }
    };

    return (
        <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Conversations</h2>
                    <p className="text-sm text-slate-500 mt-1">Manage your past research chats.</p>
                </div>
                <Link
                    to="/chat"
                    className="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 transition-colors"
                >
                    New General Chat
                </Link>
            </div>

            <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden min-h-[400px]">
                {isLoading ? (
                    <div className="flex flex-col justify-center items-center h-64 space-y-4">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                        <p className="text-sm text-slate-500">Loading conversations...</p>
                    </div>
                ) : conversations.length > 0 ? (
                    <ul role="list" className="divide-y divide-slate-200 dark:divide-slate-800">
                        {conversations.map((conv) => (
                            <li key={conv.id} className="relative flex justify-between gap-x-6 px-6 py-5 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                                <div className="flex min-w-0 gap-x-4 items-center">
                                    <div className="flex h-12 w-12 flex-none items-center justify-center rounded-lg bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400">
                                        <MessageSquare className="h-6 w-6" aria-hidden="true" />
                                    </div>
                                    <div className="min-w-0 flex-auto">
                                        <p className="text-sm font-semibold leading-6 text-slate-900 dark:text-white">
                                            <Link to={`/chat?convId=${conv.id}&docId=${conv.document_id}`} className="hover:underline">
                                                <span className="absolute inset-x-0 -top-px bottom-0" />
                                                {conv.title || 'Research Session'}
                                            </Link>
                                        </p>
                                        <div className="mt-1 flex items-center gap-x-4 text-xs leading-5 text-slate-500">
                                            <div className="flex items-center gap-1">
                                                <Calendar className="h-3.5 w-3.5" />
                                                {new Date(conv.updated_at).toLocaleDateString()}
                                            </div>
                                            <div className="flex items-center gap-1">
                                                <FileText className="h-3.5 w-3.5" />
                                                Document Chat
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex shrink-0 items-center gap-x-4 z-10 relative">
                                    <AlertDialog>
                                        <AlertDialogTrigger 
                                            disabled={isDeleting}
                                            render={<button className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-md transition-colors disabled:opacity-50" title="Delete Conversation" />}
                                        >
                                            <Trash2 className="w-5 h-5" />
                                        </AlertDialogTrigger>
                                        <AlertDialogContent>
                                            <AlertDialogHeader>
                                                <AlertDialogTitle>Delete Conversation</AlertDialogTitle>
                                                <AlertDialogDescription>
                                                    Are you sure you want to delete this conversation? This action cannot be undone.
                                                </AlertDialogDescription>
                                            </AlertDialogHeader>
                                            <AlertDialogFooter>
                                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                                <AlertDialogAction 
                                                    onClick={() => handleDelete(conv.id)}
                                                    className="bg-red-600 hover:bg-red-700"
                                                >
                                                    Delete
                                                </AlertDialogAction>
                                            </AlertDialogFooter>
                                        </AlertDialogContent>
                                    </AlertDialog>
                                </div>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <div className="flex flex-col items-center justify-center h-64 text-center px-4">
                        <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-full mb-4">
                            <MessageSquare className="w-10 h-10 text-slate-400" />
                        </div>
                        <h3 className="text-base font-semibold text-slate-900 dark:text-white">No conversations yet</h3>
                        <p className="text-sm text-slate-500 mt-1 max-w-sm">
                            Select a document to start a research session, or start a new general chat.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
