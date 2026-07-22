import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, File, AlertCircle } from 'lucide-react';

export function UploadDropzone({ onUpload, isUploading, progress }) {
    const [error, setError] = useState(null);

    const onDrop = useCallback(acceptedFiles => {
        setError(null);
        if (acceptedFiles.length === 0) return;
        
        const file = acceptedFiles[0];
        
        // Client-side validation
        if (file.type !== 'application/pdf') {
            setError("Only PDF files are supported.");
            return;
        }
        
        // Check size (25MB)
        if (file.size > 25 * 1024 * 1024) {
            setError("File exceeds the 25MB limit.");
            return;
        }

        onUpload(file);
    }, [onUpload]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
        onDrop,
        accept: { 'application/pdf': ['.pdf'] },
        maxFiles: 1,
        disabled: isUploading
    });

    return (
        <div className="w-full">
            <div 
                {...getRootProps()} 
                className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors
                    ${isDragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-gray-400'}
                    ${isUploading ? 'opacity-50 pointer-events-none' : ''}
                `}
            >
                <input {...getInputProps()} />
                <div className="flex flex-col items-center justify-center space-y-4">
                    <div className="p-4 bg-gray-50 rounded-full">
                        <UploadCloud className="w-8 h-8 text-gray-400" />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-gray-900">
                            {isDragActive ? "Drop the PDF here" : "Drag & drop a PDF, or click to select"}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">PDF up to 25MB</p>
                    </div>
                </div>
            </div>

            {error && (
                <div className="mt-4 flex items-center gap-2 text-sm text-red-600 bg-red-50 p-3 rounded-md">
                    <AlertCircle className="w-4 h-4" />
                    <span>{error}</span>
                </div>
            )}

            {isUploading && (
                <div className="mt-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                        <span>Uploading...</span>
                        <span>{Math.round(progress)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                            className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                </div>
            )}
        </div>
    );
}
