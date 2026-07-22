import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AppRouter } from './routes/AppRouter';
import { Toaster } from 'sonner';

function App() {
    return (
        <BrowserRouter>
            <Toaster position="top-right" richColors />
            <AppRouter />
        </BrowserRouter>
    );
}

export default App;
