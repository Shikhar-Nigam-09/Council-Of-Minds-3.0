import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from '../pages/auth/LoginPage';
import RegisterPage from '../pages/auth/RegisterPage';
import DashboardPage from '../pages/dashboard/DashboardPage';
import DocumentsPage from '../pages/documents/DocumentsPage';
import DocumentDetailPage from '../pages/documents/DocumentDetailPage';
import ChatPage from '../pages/chat/ChatPage';
import ConversationsPage from '../pages/conversation/ConversationsPage';
import { ProtectedRoute } from './ProtectedRoute';
import EvaluationPage from '../pages/evaluation/EvaluationPage';
import { AppLayout } from '../components/layout/AppLayout';

export const AppRouter = () => {
    const isEvaluationEnabled = import.meta.env.VITE_ENABLE_EVALUATION === 'true';

    return (
        <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            
            <Route element={<ProtectedRoute />}>
                <Route element={<AppLayout />}>
                    <Route path="/dashboard" element={<DashboardPage />} />
                    <Route path="/documents" element={<DocumentsPage />} />
                    <Route path="/documents/:id" element={<DocumentDetailPage />} />
                    <Route path="/chat" element={<ChatPage />} />
                    <Route path="/conversations" element={<ConversationsPage />} />
                    
                    {isEvaluationEnabled && (
                        <Route path="/evaluation" element={<EvaluationPage />} />
                    )}
                </Route>
            </Route>
            
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
    );
};
