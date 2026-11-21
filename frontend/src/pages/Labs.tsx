import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { errorHandler } from '../utils/errorHandler'

import { useAuth } from '../context/AuthContext'

// The /labs endpoint should return an array, but guard against unexpected
// payloads (e.g. an HTML page or a wrapped body) so rendering never crashes.
const toLabList = (data: any): any[] | null => {
    if (Array.isArray(data)) return data
    if (Array.isArray(data?.labs)) return data.labs
    if (Array.isArray(data?.data)) return data.data
    return null
}


const Labs: React.FC = () => {
    const API_BASE_URL = import.meta.env.VITE_AWVS_BASE_URL;
    const [labs, setLabs] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const { user, loading: authLoading } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        const fetchLabs = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/labs`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('auth')}`
                    }
                })
                const list = toLabList(response.data)
                if (!list) {
                    setError('Unexpected response from the server. Please try again.')
                    return
                }
                setLabs(list)
            } catch (err: any) {
                setError(errorHandler(err));
            } finally {
                setLoading(false)
            }
        }

        fetchLabs()
    }, [])

    if (loading || authLoading) {
        return (
            <div className="page-loading">
                <div className="loading-spinner-wrap">
                    <svg className="loading-spinner" viewBox="0 0 24 24">
                        <circle className="spinner-circle"></circle>
                        <path className="spinner-path"></path>
                    </svg>
                    <p className="loading-text">Loading labs...</p>
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

    return (
        <div className="labs-page">
            <div className="labs-container">
                <div className="labs-content">
                    <h1 className="page-title">Vulnerable Labs</h1>

                    <p className="page-subtitle">
                        Select a lab to launch simulated attacks against active external targets.
                    </p>

                    <div className="labs-grid">
                        {labs.map((lab: any) => (
                            <div key={lab.id} className="card lab-card">
                                <div className="card-body lab-card-body">
                                    <div className="lab-header">
                                        <h3 className="lab-title">{lab.name}</h3>
                                    </div>
                                    <p className="lab-description">{lab.description || 'No description available'}</p>

                                    <div className="lab-card-actions">
                                        <button
                                            className="btn btn-sm btn-primary"
                                            onClick={() => {
                                                if (!user) {
                                                    navigate('/login', { replace: true })
                                                } else {
                                                    navigate(`/lab/${lab.id}/attacks`)
                                                }
                                            }}
                                        >
                                            Run Attack
                                        </button>

                                        <button
                                            className="btn btn-sm btn-outline"
                                            onClick={() => {
                                                if (!user) {
                                                    navigate('/login', { replace: true })
                                                } else {
                                                    navigate(`/lab/${lab.id}`)
                                                }
                                            }}
                                        >
                                            Details
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Labs
