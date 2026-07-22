import React from 'react';
import { Type, Table, Image, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react';

const ReportItem = ({ label, status, icon: Icon }) => {
    let statusIcon;
    let statusColor;
    
    if (status === 'success') {
        statusIcon = <CheckCircle className="w-4 h-4 text-green-500" />;
        statusColor = 'text-green-700';
    } else if (status === 'failed') {
        statusIcon = <XCircle className="w-4 h-4 text-red-500" />;
        statusColor = 'text-red-700';
    } else if (status === 'skipped') {
        statusIcon = <AlertCircle className="w-4 h-4 text-gray-400" />;
        statusColor = 'text-gray-500';
    } else {
        statusIcon = <Clock className="w-4 h-4 text-yellow-500" />;
        statusColor = 'text-yellow-700';
    }

    return (
        <div className="flex items-center justify-between py-2 border-b last:border-0">
            <div className="flex items-center gap-2">
                <Icon className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">{label}</span>
            </div>
            <div className={`flex items-center gap-2 text-sm ${statusColor}`}>
                {statusIcon}
                <span className="capitalize">{status}</span>
            </div>
        </div>
    );
};

export function ProcessingReport({ report }) {
    if (!report) return <div className="text-sm text-gray-500">No processing report available.</div>;

    return (
        <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-3">Extraction Pipeline</h4>
            <div className="space-y-1">
                <ReportItem label="Text" status={report.text} icon={Type} />
                <ReportItem label="Tables" status={report.tables} icon={Table} />
                <ReportItem label="OCR" status={report.ocr} icon={Type} />
                <ReportItem label="Images" status={report.images} icon={Image} />
            </div>
        </div>
    );
}
