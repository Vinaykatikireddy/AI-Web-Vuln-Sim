import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { errorHandler } from '../utils/errorHandler'
import { retry } from '../utils/retry'
import { cancelRequest } from '../utils/cancelRequest'

const Profile: React.FC = () => {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
    const [user, setUser] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [isSaving, setIsSaving] = useState(false)
    const navigate = useNavigate()

    useEffect(() => {
        const { cancelTokenSource, cancelRequest: cancel } = cancelRequest();
        const fetchUserProfile = async () => {
            try {
                const response = await retry(() => axios.get(`${API_BASE_URL}/auth/me`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('auth')}`
                    },
                    cancelToken: cancelTokenSource.token
                }));
                setUser(response.data)
            } catch (err: any) {
                if (!axios.isCancel(err)) {
                    setError(errorHandler(err));
                }
            } finally {
                setLoading(false)
            }
        }

        fetchUserProfile();
        return cancel;
    }, [navigate])

    const handleUpdateProfile = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsSaving(true)
        const { cancelTokenSource, cancelRequest: cancel } = cancelRequest();
        try {
            const response = await retry(() => axios.put(`${API_BASE_URL}/auth/me`, {
                username: user.username,
                email: user.email
            }, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth')}`
                },
                cancelToken: cancelTokenSource.token
            }));
            setUser(response.data)
            alert('Profile updated successfully!')
        } catch (err: any) {
            if (!axios.isCancel(err)) {
                setError(errorHandler(err));
            }
        } finally {
            setIsSaving(false)
        }
    }

    const handleChangePassword = async () => {
        const currentPassword = prompt("Enter your current password:");
        if (!currentPassword) return;

        const newPassword = prompt("Enter your new password:");
        if (!newPassword) return;

        const confirmPassword = prompt("Confirm your new password:");
        if (newPassword !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }

        setIsSaving(true);
        try {
            await axios.post(
                `${API_BASE_URL}/api/auth/change-password`,
                { current_password: currentPassword, new_password: newPassword },
                {headers: {'Authorization': `Bearer ${localStorage.getItem('auth')}`}}
            );
            alert("Password changed successfully!");
        } catch (err: any) {
            setError(errorHandler(err));
        } finally {
            setIsSaving(false);
        }
    }

    const handleDeleteAccount = async () => {
        if (!window.confirm("Are you sure you want to delete your account? This action cannot be undone.")) return;

        const password = prompt("Enter your password to confirm account deletion:");
        if (!password) return;

        setIsSaving(true);
        try {
            await deleteAccount(password);
            localStorage.removeItem('auth');
            localStorage.removeItem('user');
            navigate('/login');
        } catch (err: any) {
            setError(errorHandler(err));
        } finally {
            setIsSaving(false);
        }
    }

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <svg className="animate-spin -ml-1 mr-3 h-12 w-12 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <p className="mt-4 text-gray-600">Loading profile...</p>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
                        <strong className="font-bold">Error: </strong>
                        <span className="block sm:inline">{error}</span>
                    </div>
                    <button
                        onClick={() => window.location.reload()}
                        className="mt-4 btn btn-primary"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        )
    }

    if (!user) return null

    return (
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
                <div className="border-4 border-dashed border-gray-200 rounded-lg h-full">
                    <h1 className="text-3xl font-bold text-gray-900 mb-6">Profile</h1>

                    <div className="bg-white rounded-lg shadow overflow-hidden">
                        <div className="px-6 py-5 border-b border-gray-200">
                            <h2 className="text-xl font-semibold text-gray-900">Account Information</h2>
                        </div>

                        <form onSubmit={handleUpdateProfile} className="px-6 py-5">
                            <div className="grid grid-cols-1 gap-6">
                                <div>
                                    <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                                        Username
                                    </label>
                                    <div className="mt-1">
                                        <input
                                            type="text"
                                            name="username"
                                            id="username"
                                            className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                            value={user.username}
                                            onChange={(e) => setUser({ ...user, username: e.target.value })}
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                                        Email address
                                    </label>
                                    <div className="mt-1">
                                        <input
                                            type="email"
                                            name="email"
                                            id="email"
                                            className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                            value={user.email}
                                            onChange={(e) => setUser({ ...user, email: e.target.value })}
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700">
                                        Joined on
                                    </label>
                                    <div className="mt-1">
                                        <input
                                            type="text"
                                            disabled
                                            className="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-md focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                                            value={new Date(user.created_at).toLocaleDateString()}
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="mt-6 flex justify-end">
                                <button
                                    type="submit"
                                    disabled={isSaving}
                                    className="bg-blue-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                                >
                                    {isSaving ? (
                                        <span className="flex items-center">
                                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                            </svg>
                                            Saving...
                                        </span>
                                    ) : (
                                        'Save Changes'
                                    )}
                                </button>
                            </div>
                        </form>

                        <div className="px-6 py-5 border-t border-gray-200">
                            <h2 className="text-xl font-semibold text-gray-900 mb-4">Security</h2>

                            <div className="grid grid-cols-1 gap-6">
                                 <div className="bg-gray-50 rounded-lg p-4">
                                     <h3 className="text-lg font-medium text-gray-900 mb-2">Password</h3>
                                     <p className="text-gray-600 mb-4">Update your account password.</p>
                                     <button
                                         onClick={handleChangePassword}
                                         disabled={isSaving}
                                         className="bg-gray-100 text-gray-700 py-2 px-4 rounded-md text-sm font-medium hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50"
                                     >
                                         {isSaving ? 'Processing...' : 'Change Password'}
                                     </button>
                                 </div>
                            </div>
                        </div>

                        <div className="px-6 py-5 border-t border-gray-200">
                            <h2 className="text-xl font-semibold text-gray-900 mb-4">Account Actions</h2>

                            <div className="grid grid-cols-1 gap-6">
                                 <div className="bg-gray-50 rounded-lg p-4">
                                     <h3 className="text-lg font-medium text-gray-900 mb-2">Delete Account</h3>
                                     <p className="text-gray-600 mb-4">Permanently delete your account and all associated data. This action cannot be undone.</p>
                                     <button
                                         onClick={handleDeleteAccount}
                                         disabled={isSaving}
                                         className="bg-red-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50"
                                     >
                                         {isSaving ? 'Processing...' : 'Delete Account'}
                                     </button>
                                 </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Profile