import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { errorHandler } from '../utils/errorHandler'
import logoSvg from '../logo.svg';

const Register: React.FC = () => {
    const API_BASE_URL = import.meta.env.VITE_AWVS_BASE_URL;
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    })
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)
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
        setLoading(true)

        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match')
            setLoading(false)
            return
        }

        try {
            const response = await axios.post(`${API_BASE_URL}/auth/register`, {
                username: formData.username,
                email: formData.email,
                password: formData.password
            })

            setLoading(false)
            setLoading(false)

            navigate("/login", {
                state: {
                    successMessage: response.data.message || 'Account created successfully. Please login.'
                }
            })
        } catch (err: any) {
            setLoading(false)
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
                        Create your account
                    </h2>
                    <p className="auth-subtitle">
                        Or{' '}
                        <Link
                            to="/login"
                            className="auth-link"
                        >
                            sign in to your existing account
                        </Link>
                    </p>
                </div>
                <form className="auth-form" onSubmit={handleSubmit}>
                    {error && (
                        <div className="alert alert-error">
                            <div className="alert-content">{error}</div>
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
                            <label htmlFor="email" className="form-label">
                                Email address
                            </label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                autoComplete="email"
                                required
                                className="form-input"
                                placeholder="Email address"
                                value={formData.email}
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
                                autoComplete="new-password"
                                required
                                className="form-input"
                                placeholder="Password"
                                value={formData.password}
                                onChange={handleChange}
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="confirmPassword" className="form-label">
                                Confirm Password
                            </label>
                            <input
                                id="confirmPassword"
                                name="confirmPassword"
                                type="password"
                                autoComplete="new-password"
                                required
                                className="form-input"
                                placeholder="Confirm Password"
                                value={formData.confirmPassword}
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
                                    Creating account...
                                </span>
                            ) : (
                                'Create account'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}

export default Register
