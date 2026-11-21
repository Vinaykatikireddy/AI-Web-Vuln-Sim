import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { errorHandler } from '../utils/errorHandler'
import { retry } from '../utils/retry'
import { cancelRequest } from '../utils/cancelRequest'

const Profile: React.FC = () => {
    const API_BASE_URL = import.meta.env.VITE_AWVS_BASE_URL;
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
            const response = await retry(() => axios.patch(`${API_BASE_URL}/auth/update-user`, {
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
                `${API_BASE_URL}/auth/change-password`,
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
            await axios.delete(`${API_BASE_URL}/auth/delete-account`, {
                data: { password },
                headers: { 'Authorization': `Bearer ${localStorage.getItem('auth')}` }
            });
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
            <div className="page-loading">
                <div className="loading-spinner-wrap">
                    <svg className="loading-spinner" viewBox="0 0 24 24">
                        <circle className="spinner-circle"></circle>
                        <path className="spinner-path"></path>
                    </svg>
                    <p className="loading-text">Loading profile...</p>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="alert alert-error">
                <div className="alert-content">
                    <strong className="alert-title">Error: </strong>
                    <span className="alert-message">{error}</span>
                </div>
                <button
                    onClick={() => window.location.reload()}
                    className="btn btn-sm btn-outline"
                >
                    Try Again
                </button>
            </div>
        )
    }

    if (!user) return null

    return (
        <div className="profile-page">
            <div className="profile-container">
                <div className="profile-content">
                    <h1 className="page-title">Profile</h1>

                    <div className="profile-sections">
                        <div className="card profile-card">
                            <div className="card-header">
                                <h2 className="card-title">Account Information</h2>
                            </div>

                            <form onSubmit={handleUpdateProfile} className="card-body profile-form">
                                <div className="form-grid">
                                    <div className="form-group">
                                        <label htmlFor="username" className="form-label">
                                            Username
                                        </label>
                                        <input
                                            type="text"
                                            name="username"
                                            id="username"
                                            className="form-input"
                                            value={user.username}
                                            onChange={(e) => setUser({ ...user, username: e.target.value })}
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label htmlFor="email" className="form-label">
                                            Email address
                                        </label>
                                        <input
                                            type="email"
                                            name="email"
                                            id="email"
                                            className="form-input"
                                            value={user.email}
                                            onChange={(e) => setUser({ ...user, email: e.target.value })}
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">
                                            Joined on
                                        </label>
                                        <input
                                            type="text"
                                            disabled
                                            className="form-input form-input-disabled"
                                            value={new Date(user.created_at).toLocaleDateString()}
                                        />
                                    </div>
                                </div>

                                <div className="form-actions">
                                    <button
                                        type="submit"
                                        disabled={isSaving}
                                        className="btn btn-primary"
                                    >
                                        {isSaving ? (
                                            <span className="btn-loading">
                                                <svg className="loading-spinner-sm" viewBox="0 0 24 24">
                                                    <circle className="spinner-circle"></circle>
                                                    <path className="spinner-path"></path>
                                                </svg>
                                                Saving...
                                            </span>
                                        ) : (
                                            'Save Changes'
                                        )}
                                    </button>
                                </div>
                            </form>
                        </div>

                        <div className="card profile-card">
                            <div className="card-header">
                                <h2 className="card-title">Security</h2>
                            </div>

                            <div className="card-body">
                                <div className="action-row">
                                    <div className="action-info">
                                        <h3 className="action-title">Password</h3>
                                        <p className="action-desc">Update your account password.</p>
                                    </div>
                                    <button
                                        onClick={handleChangePassword}
                                        disabled={isSaving}
                                        className="btn btn-outline"
                                    >
                                        {isSaving ? 'Processing...' : 'Change Password'}
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div className="card profile-card card-danger">
                            <div className="card-header">
                                <h2 className="card-title text-danger">Account Actions</h2>
                            </div>

                            <div className="card-body">
                                <div className="action-row">
                                    <div className="action-info">
                                        <h3 className="action-title">Delete Account</h3>
                                        <p className="action-desc">Permanently delete your account and all associated data. This action cannot be undone.</p>
                                    </div>
                                    <button
                                        onClick={handleDeleteAccount}
                                        disabled={isSaving}
                                        className="btn btn-danger"
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
