import React, { useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { LayoutDashboard, Files, MessageSquare, LogOut, Menu, X, User } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { useAuth } from '../../features/auth/useAuth';

export const AppLayout = () => {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const { user } = useAuthStore();
    const { logout } = useAuth();
    const location = useLocation();

    const navigation = [
        { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
        { name: 'Documents', href: '/documents', icon: Files },
        { name: 'Chat', href: '/chat', icon: MessageSquare },
        { name: 'Conversations', href: '/conversations', icon: MessageSquare },
    ];

    const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
    const closeSidebar = () => setSidebarOpen(false);

    // Logic for active navigation
    const isActive = (item) => {
        if (item.href === '/chat' && location.pathname.includes('/chat')) return true;
        if (item.name === 'Documents' && location.pathname.includes('/chat')) return false;
        return location.pathname.startsWith(item.href);
    };

    const SidebarContent = () => (
        <div className="flex h-full flex-col bg-slate-900 border-r border-slate-800 text-slate-100">
            <div className="flex h-16 shrink-0 items-center px-6 border-b border-slate-800">
                <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500 font-bold text-white shadow-sm shadow-indigo-500/20">
                        C
                    </div>
                    <span className="text-lg font-semibold tracking-tight text-white">Council of Minds</span>
                </div>
            </div>

            <nav className="flex flex-1 flex-col px-4 py-6 overflow-y-auto">
                <ul role="list" className="flex flex-1 flex-col gap-y-7">
                    <li>
                        <div className="text-xs font-semibold leading-6 text-slate-400 mb-2 px-2 uppercase tracking-wider">
                            Main Navigation
                        </div>
                        <ul role="list" className="-mx-2 space-y-1">
                            {navigation.map((item) => (
                                <li key={item.name}>
                                    <NavLink
                                        to={item.href}
                                        onClick={closeSidebar}
                                        className={({ isActive: isExactActive }) => {
                                            const active = isActive(item);
                                            return `
                                                group flex gap-x-3 rounded-md p-2 text-sm font-medium leading-6 transition-colors
                                                ${active 
                                                    ? 'bg-slate-800 text-white' 
                                                    : 'text-slate-300 hover:bg-slate-800/50 hover:text-white'}
                                            `;
                                        }}
                                    >
                                        <item.icon className="h-5 w-5 shrink-0 opacity-70 group-hover:opacity-100" aria-hidden="true" />
                                        {item.name}
                                    </NavLink>
                                </li>
                            ))}
                        </ul>
                    </li>
                </ul>
            </nav>

            <div className="mt-auto border-t border-slate-800 p-4">
                <div className="flex items-center gap-x-4 px-2 py-3 rounded-md bg-slate-800/50 mb-4">
                    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-700">
                        <User className="h-5 w-5 text-slate-300" />
                    </div>
                    <div className="flex flex-col min-w-0">
                        <span className="truncate text-sm font-medium text-white">{user?.full_name || 'User'}</span>
                        <span className="truncate text-xs text-slate-400">{user?.email}</span>
                    </div>
                </div>
                <button
                    onClick={() => logout.mutate()}
                    className="flex w-full items-center gap-x-3 rounded-md px-2 py-2 text-sm font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
                >
                    <LogOut className="h-5 w-5 shrink-0 opacity-70" />
                    Sign Out
                </button>
            </div>
        </div>
    );

    return (
        <div className="flex h-screen w-full bg-slate-50 dark:bg-slate-950">
            {/* Desktop Sidebar */}
            <div className="hidden lg:flex lg:w-72 lg:flex-col lg:fixed lg:inset-y-0 z-50">
                <SidebarContent />
            </div>

            {/* Mobile Sidebar Overlay */}
            {sidebarOpen && (
                <div className="relative z-50 lg:hidden">
                    <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm transition-opacity" onClick={closeSidebar} />
                    <div className="fixed inset-0 flex">
                        <div className="relative mr-16 flex w-full max-w-xs flex-1 transform transition duration-300 ease-in-out">
                            <div className="absolute left-full top-0 flex w-16 justify-center pt-5">
                                <button type="button" className="-m-2.5 p-2.5" onClick={closeSidebar}>
                                    <span className="sr-only">Close sidebar</span>
                                    <X className="h-6 w-6 text-white" aria-hidden="true" />
                                </button>
                            </div>
                            <SidebarContent />
                        </div>
                    </div>
                </div>
            )}

            {/* Main Content Area */}
            <div className="flex flex-1 flex-col lg:pl-72 w-full h-full">
                {/* Mobile Header */}
                <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-slate-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:hidden dark:bg-slate-900 dark:border-slate-800">
                    <button type="button" className="-m-2.5 p-2.5 text-slate-700 dark:text-slate-200" onClick={toggleSidebar}>
                        <span className="sr-only">Open sidebar</span>
                        <Menu className="h-6 w-6" aria-hidden="true" />
                    </button>
                    <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
                        <div className="flex flex-1 items-center font-semibold text-slate-900 dark:text-white">
                            Council of Minds
                        </div>
                    </div>
                </div>

                {/* Page Content */}
                <main className="flex-1 overflow-y-auto">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};
