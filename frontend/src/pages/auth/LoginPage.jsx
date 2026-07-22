import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from 'react-router-dom';
import { loginSchema } from '../../features/auth/authSchemas';
import { useAuth } from '../../features/auth/useAuth';
import { toast } from 'sonner';
import { Loader2, Mail, Lock } from 'lucide-react';

export default function LoginPage() {
    const { login } = useAuth();
    
    const {
        register,
        handleSubmit,
        formState: { errors }
    } = useForm({
        resolver: zodResolver(loginSchema),
        defaultValues: { email: '', password: '' }
    });

    const onSubmit = (data) => {
        login.mutate(data, {
            onSuccess: () => {
                toast.success("Successfully signed in");
            },
            onError: (error) => {
                console.error(error);
                toast.error(error.response?.data?.error?.message || "Login failed. Please check your credentials.");
            }
        });
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-slate-50 dark:bg-slate-950 px-4 sm:px-6 lg:px-8">
            <div className="w-full max-w-md space-y-8 rounded-2xl bg-white dark:bg-slate-900 p-8 sm:p-10 shadow-xl ring-1 ring-slate-200 dark:ring-slate-800">
                <div className="text-center">
                    <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-600 shadow-sm mb-4">
                        <span className="text-xl font-bold text-white">C</span>
                    </div>
                    <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Welcome Back</h2>
                    <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">Sign in to your Council of Minds account</p>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Email address</label>
                            <div className="relative mt-2 rounded-md shadow-sm">
                                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                                    <Mail className="h-5 w-5 text-slate-400" aria-hidden="true" />
                                </div>
                                <input
                                    {...register('email')}
                                    className="block w-full rounded-lg border-0 py-2.5 pl-10 text-slate-900 ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 dark:bg-slate-800 dark:text-white dark:ring-slate-700"
                                    placeholder="you@example.com"
                                    type="email"
                                />
                            </div>
                            {errors.email && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.email.message}</p>}
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Password</label>
                            <div className="relative mt-2 rounded-md shadow-sm">
                                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                                    <Lock className="h-5 w-5 text-slate-400" aria-hidden="true" />
                                </div>
                                <input
                                    {...register('password')}
                                    className="block w-full rounded-lg border-0 py-2.5 pl-10 text-slate-900 ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 dark:bg-slate-800 dark:text-white dark:ring-slate-700"
                                    placeholder="••••••••"
                                    type="password"
                                />
                            </div>
                            {errors.password && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.password.message}</p>}
                        </div>
                    </div>
                    
                    <button
                        type="submit"
                        disabled={login.isPending}
                        className="flex w-full justify-center items-center rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition-colors disabled:opacity-50"
                    >
                        {login.isPending ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Signing in...
                            </>
                        ) : 'Sign in'}
                    </button>
                    
                    <div className="text-center text-sm">
                        <span className="text-slate-600 dark:text-slate-400">Don't have an account? </span>
                        <Link to="/register" className="font-semibold text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300 transition-colors">
                            Sign up now
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    );
}
