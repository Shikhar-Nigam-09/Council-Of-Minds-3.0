import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Loader2 } from 'lucide-react';

export function StatusBadge({ status }) {
    switch (status) {
        case 'uploaded':
            return <Badge variant="secondary">Uploaded</Badge>;
        case 'queued':
            return (
                <Badge variant="outline" className="text-blue-600 border-blue-200 bg-blue-50">
                    Queued
                </Badge>
            );
        case 'processing':
            return (
                <Badge variant="outline" className="text-blue-600 border-blue-200 bg-blue-50 gap-1">
                    <Loader2 className="w-3 h-3 animate-spin" />
                    Processing
                </Badge>
            );
        case 'partial':
            return (
                <Badge variant="outline" className="text-amber-600 border-amber-200 bg-amber-50">
                    Partial
                </Badge>
            );
        case 'completed':
            return (
                <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50">
                    Completed
                </Badge>
            );
        case 'failed':
            return <Badge variant="destructive">Failed</Badge>;
        default:
            return <Badge variant="outline">{status}</Badge>;
    }
}
