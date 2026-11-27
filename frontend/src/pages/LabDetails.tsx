import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import axios from 'axios'
import { errorHandler } from '../utils/errorHandler'

const LabDetails: React.FC = () => {
    const API_BASE_URL = import.meta.env.VITE_AWVS_BASE_URL;
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const [lab, setLab] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [togglingComplete, setTogglingComplete] = useState(false)
    const [toggleError, setToggleError] = useState('')

    useEffect(() => {
        const fetchLab = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/labs/${id}`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('auth')}`
                    }
                })
                setLab(response.data)
            } catch (err: any) {
                setError(errorHandler(err));
            } finally {
                setLoading(false)
            }
        }

        fetchLab()
    }, [id, navigate])

    if (loading) {
        return (
            <div className="page-loading">
                <div className="loading-spinner-wrap">
                    <svg className="loading-spinner" viewBox="0 0 24 24">
                        <circle className="spinner-circle"></circle>
                        <path className="spinner-path"></path>
                    </svg>
                    <p className="loading-text">Loading lab details...</p>
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
                    onClick={() => navigate(-1)}
                    className="btn btn-sm btn-outline"
                >
                    Back to Labs
                </button>
            </div>
        )
    }

    if (!lab) return null

    const handleToggleComplete = async () => {
        setTogglingComplete(true)
        setToggleError('')
        try {
            const response = await axios.post(
                `${API_BASE_URL}/labs/${lab.id}/complete`,
                {},
                {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('auth')}`
                    }
                }
            )
            setLab((prev: any) => ({
                ...prev,
                completed: response.data.completed
            }))
        } catch (err: any) {
            setToggleError(errorHandler(err))
        } finally {
            setTogglingComplete(false)
        }
    }

    const vulnerabilityIcons: Record<string, JSX.Element> = {
        'SQL Injection': <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>,
        'XSS': <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>,
        'IDOR': <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>,
        'File Upload': <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
    }

    const vulnerabilityMap: Record<string, string[]> = {
        'Simple Login': ['SQL Injection'],
        'Blog': ['XSS'],
        'Ecommerce': ['IDOR'],
        'File Upload': ['File Upload']
    }

    return (
        <div className="lab-details-page">
            <div className="lab-details-container">
                <div className="lab-details-content">
                    <div className="page-header-row">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                            <button
                                onClick={() => navigate('/labs')}
                                className="btn-icon"
                                aria-label="Back to labs"
                            >
                                <svg className="icon-back" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
                                </svg>
                            </button>
                            <h1 className="page-title">{lab.name}</h1>
                        </div>

                        <label
                            className={`lab-complete-toggle ${lab.completed ? 'is-completed' : ''} ${togglingComplete ? 'is-disabled' : ''}`}
                        >
                            <input
                                type="checkbox"
                                className="lab-complete-input"
                                checked={Boolean(lab.completed)}
                                onChange={handleToggleComplete}
                                disabled={togglingComplete}
                            />
                            <span className="lab-complete-box" aria-hidden="true">
                                {lab.completed && (
                                    <svg className="lab-complete-check" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                    </svg>
                                )}
                            </span>
                            <span>
                                {togglingComplete
                                    ? 'Updating...'
                                    : lab.completed
                                    ? 'Completed'
                                    : 'Mark as completed'}
                            </span>
                        </label>
                    </div>
                    {toggleError && (
                        <p className="alert-message" style={{ color: 'var(--color-danger, #f87171)', marginBottom: '1rem' }}>
                            {toggleError}
                        </p>
                    )}

                    <div className="lab-details-grid">
                        <div className="card lab-main-card">
                            <div className="card-body">
                                <div>
                                    <div className="lab-status-banner">
                                        <p className="lab-desc-lead">{lab.description || 'No description available'}</p>
                                    </div>

                                    <div className="info-block">
                                        <h4 className="info-label">Description</h4>
                                        <p className="info-text">{lab.description || 'No detailed description available for this lab.'}</p>
                                    </div>

                                    <div className="lab-actions-bar">
                                        <Link
                                            to={`/lab/${lab.id}/attacks`}
                                            className="btn btn-primary"
                                        >
                                            Run Attack
                                        </Link>

                                        {lab.external_url && (
                                            <a
                                                href={lab.external_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="btn btn-outline"
                                            >
                                                Visit Target Site ↗
                                            </a>
                                        )}
                                    </div>
                                </div>

                                <div className="mt-6">
                                    <h3 className="section-heading">Vulnerabilities</h3>
                                    <div className="vulnerability-tags">
                                        {(vulnerabilityMap[lab.name] || []).map((vuln) => (
                                            <span key={vuln} className="vuln-tag">
                                                <span className="vuln-icon">{vulnerabilityIcons[vuln]}</span>
                                                <span className="vuln-text">{vuln}</span>
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="card lab-info-card">
                            <div className="card-header">
                                <h3 className="card-title">Lab Details</h3>
                            </div>
                            <div className="card-body">
                                <div className="info-grid">
                                    <div className="info-item">
                                        <h4 className="info-label">Target URL</h4>
                                        <p className="info-value font-mono">
                                            {lab.external_url ? (
                                                <a
                                                    href={lab.external_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    style={{ color: '#60a5fa', textDecoration: 'underline', wordBreak: 'break-all' }}
                                                >
                                                    {lab.external_url}
                                                </a>
                                            ) : (
                                                'N/A'
                                            )}
                                        </p>
                                    </div>

                                    <div className="info-item">
                                        <h4 className="info-label">Lab Type</h4>
                                        <p className="info-value">Web application vulnerability lab</p>
                                    </div>
                                </div>

                                <div className="security-notice-box">
                                    <h4 className="notice-title">Security Note</h4>
                                    <p className="notice-text">This lab is purposefully vulnerable to help you learn cybersecurity practices. Only use it for educational purposes within this platform.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default LabDetails
