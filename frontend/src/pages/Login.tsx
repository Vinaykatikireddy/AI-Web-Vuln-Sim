import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { errorHandler } from '../utils/errorHandler'
import logoSvg from '../logo.svg';

const Login: React.FC = () => {
    const [formData, setFormData] = useState({
        username: '',
        password: ''
    })
    const [error, setError] = useState('')
    const { login, loading } = useAuth()
    const navigate = useNavigate()

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        })
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        try {
            await login(formData.username, formData.password, navigate)
        } catch (err: any) {
            setError(errorHandler(err));
        }
    }

    return (
        <div className="auth-page">
            <div className="auth-card">
                <div className="auth-header">
                    <img
                        className="auth-logo"
                        src={logoSvg}
                        alt="Attack Simulation Platform"
                    />
                    <h2 className="auth-title">
                        Sign in to your account
                    </h2>
                    <p className="auth-subtitle">
                        Or{' '}
                        <Link
                            to="/register"
                            className="auth-link"
                        >
                            create a new account
                        </Link>
                    </p>
                </div>
                <form className="auth-form" onSubmit={handleSubmit}>
                    {error && (
                        <div className="alert alert-error">
                            <div className="alert-content">
                                <strong className="alert-title">Error: </strong>
                                <span className="alert-message">{error}</span>
                            </div>
                        </div>
                    )}
                    <div className="form-fields">
                        <div className="form-group">
                            <label htmlFor="username" className="form-label">
                                Username
                            </label>
                            <input
                                id="username"
                                name="username"
                                type="text"
                                autoComplete="username"
                                required
                                className="form-input"
                                placeholder="Username"
                                value={formData.username}
                                onChange={handleChange}
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="password" className="form-label">
                                Password
                            </label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                autoComplete="current-password"
                                required
                                className="form-input"
                                placeholder="Password"
                                value={formData.password}
                                onChange={handleChange}
                            />
                        </div>
                    </div>

                    <div className="form-actions">
                        <button
                            type="submit"
                            disabled={loading}
                            className="btn btn-primary btn-block btn-lg"
                        >
                            {loading ? (
                                <span className="btn-loading">
                                    <svg className="loading-spinner-sm" viewBox="0 0 24 24">
                                        <circle className="spinner-circle"></circle>
                                        <path className="spinner-path"></path>
                                    </svg>
                                    Signing in...
                                </span>
                            ) : (
                                'Sign in'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}

export default Login
