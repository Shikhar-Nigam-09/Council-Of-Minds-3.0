import React from 'react';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import { FileText, Trash2, AlertCircle, MessageSquare } from 'lucide-react';
import { StatusBadge } from './StatusBadge';
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

export function DocumentCard({ document, onDelete, isDeleting }) {
    const fileSizeMB = (document.file_size_bytes / (1024 * 1024)).toFixed(2);
    
    return (
        <div className="group relative flex items-center justify-between p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm hover:shadow-md transition-all">
            <div className="flex items-center gap-5 min-w-0">
                <div className="flex-shrink-0 p-3 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-lg">
                    <FileText className="w-7 h-7" />
                </div>
                <div className="space-y-1 min-w-0">
                    <Link to={`/documents/${document.id}`} className="font-semibold text-slate-900 dark:text-slate-100 hover:text-indigo-600 dark:hover:text-indigo-400 truncate block">
                        {document.filename}
                    </Link>
                    <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
                        <span>{fileSizeMB} MB</span>
                        <span>•</span>
                        <span>{format(new Date(document.created_at), 'MMM d, yyyy')}</span>
                        {document.page_count > 0 && (
                            <>
                                <span>•</span>
                                <span>{document.page_count} pages</span>
                            </>
                        )}
                    </div>
                    {document.error_message && (
                        <div className="flex items-center gap-1.5 text-xs text-red-600 dark:text-red-400 mt-1">
                            <AlertCircle className="w-3.5 h-3.5" />
                            <span className="truncate max-w-[250px]">{document.error_message}</span>
                        </div>
                    )}
                </div>
            </div>
            
            <div className="flex items-center gap-5 flex-shrink-0 ml-4">
                <div className="hidden sm:block">
                    <StatusBadge status={document.status} />
                </div>
                
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    {(document.status === 'completed' || document.status === 'partial') && (
                        <Link 
                            to={`/documents/${document.id}/chat`}
                            className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 rounded-md transition-colors"
                            title="Start AI Chat"
                        >
                            <MessageSquare className="w-5 h-5" />
                        </Link>
                    )}
                    
                    <AlertDialog>
                        <AlertDialogTrigger 
                            disabled={isDeleting}
                            render={<button className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-md transition-colors disabled:opacity-50" title="Delete Document" />}
                        >
                            <Trash2 className="w-5 h-5" />
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                            <AlertDialogHeader>
                                <AlertDialogTitle>Delete Document</AlertDialogTitle>
                                <AlertDialogDescription>
                                    Are you sure you want to delete <strong>{document.filename}</strong>? 
                                    This action cannot be undone.
                                </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction 
                                    onClick={() => onDelete(document.id)}
                                    className="bg-red-600 hover:bg-red-700"
                                >
                                    Delete
                                </AlertDialogAction>
                            </AlertDialogFooter>
                        </AlertDialogContent>
                    </AlertDialog>
                </div>
                {/* Mobile status badge fallback */}
                <div className="sm:hidden block">
                     <StatusBadge status={document.status} />
                </div>
            </div>
        </div>
    );
}
