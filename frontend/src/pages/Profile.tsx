import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { errorHandler } from '../utils/errorHandler'
import { retry } from '../utils/retry'
import { cancelRequest } from '../utils/cancelRequest'
import { useAuth } from '../context/AuthContext'

const Profile: React.FC = () => {
    const API_BASE_URL = import.meta.env.VITE_AWVS_BASE_URL;
    const { updateSession, logout } = useAuth();
    const [user, setUser] = useState<any>(null)
    const [initialUser, setInitialUser] = useState<{ username: string; email: string } | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [profileError, setProfileError] = useState('')
    const [profileSuccess, setProfileSuccess] = useState('')
    const [deleteError, setDeleteError] = useState('')
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
    const [deletePassword, setDeletePassword] = useState('')
    const [isDeleting, setIsDeleting] = useState(false)
    const [isSaving, setIsSaving] = useState(false)
    const [newPassword, setNewPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [passwordError, setPasswordError] = useState('')
    const [passwordSuccess, setPasswordSuccess] = useState('')
    const [isChangingPassword, setIsChangingPassword] = useState(false)
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
                setInitialUser({
                    username: response.data.username,
                    email: response.data.email
                })
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
        setProfileError('')
        setProfileSuccess('')

        const trimmedUsername = (user?.username ?? '').trim()
        const trimmedEmail = (user?.email ?? '').trim()

        if (
            initialUser &&
            trimmedUsername === initialUser.username &&
            trimmedEmail === initialUser.email
        ) {
            return
        }

        setIsSaving(true)
        const { cancelTokenSource } = cancelRequest();
        try {
            const response = await retry(() => axios.patch(`${API_BASE_URL}/auth/update-user`, {
                username: trimmedUsername,
                email: trimmedEmail
            }, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth')}`
                },
                cancelToken: cancelTokenSource.token
            }));
            const { access_token, token_type, ...updatedUser } = response.data
            setUser(updatedUser)
            setInitialUser({
                username: updatedUser.username,
                email: updatedUser.email
            })
            updateSession(access_token ?? null, {
                username: updatedUser.username,
                email: updatedUser.email
            })
            setProfileSuccess('Profile updated successfully!')
        } catch (err: any) {
            if (!axios.isCancel(err)) {
                setProfileError(errorHandler(err));
            }
        } finally {
            setIsSaving(false)
        }
    }

    const handleChangePassword = async (e: React.FormEvent) => {
        e.preventDefault();
        setPasswordError('');
        setPasswordSuccess('');

        if (!newPassword) {
            setPasswordError('Please enter a new password.');
            return;
        }

        if (newPassword !== confirmPassword) {
            setPasswordError('Passwords do not match.');
            return;
        }

        setIsChangingPassword(true);
        try {
            await axios.post(
                `${API_BASE_URL}/auth/change-password`,
                { new_password: newPassword },
                { headers: { 'Authorization': `Bearer ${localStorage.getItem('auth')}` } }
            );
            setNewPassword('');
            setConfirmPassword('');
            setPasswordSuccess('Password changed successfully!');
        } catch (err: any) {
            setPasswordError(errorHandler(err));
        } finally {
            setIsChangingPassword(false);
        }
    }

    const handleDeleteAccount = async (e: React.FormEvent) => {
        e.preventDefault();
        setDeleteError('');

        if (!deletePassword) {
            setDeleteError('Please enter your password to confirm account deletion.');
            return;
        }

        setIsDeleting(true);
        try {
            await axios.delete(`${API_BASE_URL}/auth/delete-account`, {
                data: { password: deletePassword },
                headers: { 'Authorization': `Bearer ${localStorage.getItem('auth')}` }
            });
            await logout(navigate);
        } catch (err: any) {
            setDeleteError(errorHandler(err));
        } finally {
            setIsDeleting(false);
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
                                {profileError && (
                                    <div className="alert alert-error">
                                        <div className="alert-content">
                                            <strong className="alert-title">Error: </strong>
                                            <span className="alert-message">{profileError}</span>
                                        </div>
                                    </div>
                                )}

                                {profileSuccess && (
                                    <div className="alert alert-success">
                                        <div className="alert-content">
                                            <span className="alert-message">{profileSuccess}</span>
                                        </div>
                                    </div>
                                )}

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
                                            value={new Date(user.created_at).toLocaleDateString('en-GB')}
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

                            <form onSubmit={handleChangePassword} className="card-body profile-form">
                                {passwordError && (
                                    <div className="alert alert-error">
                                        <div className="alert-content">
                                            <strong className="alert-title">Error: </strong>
                                            <span className="alert-message">{passwordError}</span>
                                        </div>
                                    </div>
                                )}

                                {passwordSuccess && (
                                    <div className="alert alert-success">
                                        <div className="alert-content">
                                            <span className="alert-message">{passwordSuccess}</span>
                                        </div>
                                    </div>
                                )}

                                <div className="form-grid">
                                    <div className="form-group">
                                        <label htmlFor="new-password" className="form-label">
                                            New Password
                                        </label>
                                        <input
                                            type="password"
                                            name="newPassword"
                                            id="new-password"
                                            className="form-input"
                                            placeholder="Enter new password"
                                            value={newPassword}
                                            onChange={(e) => setNewPassword(e.target.value)}
                                            required
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label htmlFor="confirm-password" className="form-label">
                                            Confirm New Password
                                        </label>
                                        <input
                                            type="password"
                                            name="confirmPassword"
                                            id="confirm-password"
                                            className="form-input"
                                            placeholder="Confirm new password"
                                            value={confirmPassword}
                                            onChange={(e) => setConfirmPassword(e.target.value)}
                                            required
                                        />
                                    </div>
                                </div>

                                <div className="form-actions">
                                    <button
                                        type="submit"
                                        disabled={isChangingPassword}
                                        className="btn btn-primary"
                                    >
                                        {isChangingPassword ? 'Confirming...' : 'Confirm'}
                                    </button>
                                </div>
                            </form>
                        </div>

                        <div className="card profile-card card-danger">
                            <div className="card-header">
                                <h2 className="card-title text-danger">Account Actions</h2>
                            </div>

                            <div className="card-body">
                                {deleteError && (
                                    <div className="alert alert-error">
                                        <div className="alert-content">
                                            <strong className="alert-title">Error: </strong>
                                            <span className="alert-message">{deleteError}</span>
                                        </div>
                                    </div>
                                )}
                                <div className="action-row">
                                    <div className="action-info">
                                        <h3 className="action-title">Delete Account</h3>
                                        <p className="action-desc">Permanently delete your account and all associated data. This action cannot be undone.</p>
                                    </div>
                                    {!showDeleteConfirm && (
                                        <button
                                            type="button"
                                            onClick={() => {
                                                setDeleteError('');
                                                setDeletePassword('');
                                                setShowDeleteConfirm(true);
                                            }}
                                            disabled={isDeleting}
                                            className="btn btn-danger"
                                        >
                                            Delete Account
                                        </button>
                                    )}
                                </div>

                                {showDeleteConfirm && (
                                    <form onSubmit={handleDeleteAccount} className="profile-form" style={{ marginTop: '1rem' }}>
                                        <div className="form-group">
                                            <label htmlFor="delete-password" className="form-label">
                                                Confirm with your password
                                            </label>
                                            <input
                                                type="password"
                                                id="delete-password"
                                                className="form-input"
                                                placeholder="Enter your password"
                                                value={deletePassword}
                                                onChange={(e) => setDeletePassword(e.target.value)}
                                                required
                                            />
                                        </div>
                                        <div className="form-actions" style={{ display: 'flex', gap: '0.75rem' }}>
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    setShowDeleteConfirm(false);
                                                    setDeletePassword('');
                                                    setDeleteError('');
                                                }}
                                                disabled={isDeleting}
                                                className="btn btn-outline"
                                            >
                                                Cancel
                                            </button>
                                            <button
                                                type="submit"
                                                disabled={isDeleting}
                                                className="btn btn-danger"
                                            >
                                                {isDeleting ? 'Deleting...' : 'Confirm Delete'}
                                            </button>
                                        </div>
                                    </form>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Profile
