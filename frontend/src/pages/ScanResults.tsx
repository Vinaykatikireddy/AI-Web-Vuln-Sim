import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { errorHandler } from '../utils/errorHandler'

const ScanResults: React.FC = () => {
    const API_BASE_URL = import.meta.env.VITE_AWVS_BASE_URL;
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const [scan, setScan] = useState<any>(null)
    const [logs, setLogs] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [isAnalyzing, setIsAnalyzing] = useState(false)

    useEffect(() => {
        const fetchScanData = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/scans/${id}`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('auth')}`
                    }
                })
                setScan(response.data)

                // Fetch logs
                const logsResponse = await axios.get(`${API_BASE_URL}/logs?scan_id=${id}`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('auth')}`
                    }
                })
                setLogs(logsResponse.data)
            } catch (err: any) {
                setError(errorHandler(err));
            } finally {
                setLoading(false)
            }
        }

        fetchScanData()
    }, [id, navigate])

    const analyzeScan = async () => {
        setIsAnalyzing(true)
        try {
            await axios.post(`${API_BASE_URL}/ai/analyze`, { scan_id: parseInt(id!) }, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth')}`
                }
            })

            // Refresh scan data to show updated status
            const response = await axios.get(`${API_BASE_URL}/scans/${id}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth')}`
                }
            })
            setScan(response.data)

            // Show success message
            alert('AI analysis queued successfully. Check back in a few seconds for results.')
        } catch (err: any) {
            setError(errorHandler(err));
        } finally {
            setIsAnalyzing(false)
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
                    <p className="loading-text">Loading scan results...</p>
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
                    Back to Dashboard
                </button>
            </div>
        )
    }

    if (!scan || !logs) return null

    const getStatusBadgeClass = (status: string) => {
        switch (status) {
            case 'success': return 'badge-success'
            case 'failure': return 'badge-danger'
            case 'vulnerability_detected': return 'badge-danger'
            default: return 'badge-neutral'
        }
    }

    return (
        <div className="scan-results-page">
            <div className="scan-results-container">
                <div className="scan-results-content">
                    <div className="page-header-row">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                            <button
                                onClick={() => navigate(-1)}
                                className="btn-icon"
                                aria-label="Back"
                            >
                                <svg className="icon-back" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
                                </svg>
                            </button>
                            <h1 className="page-title">Scan Results</h1>
                        </div>
                    </div>

                    <div className="card scan-card">
                        <div className="card-header scan-header">
                            <div className="scan-header-inner">
                                <div>
                                    <h2 className="scan-lab-title">{scan.lab.name}</h2>
                                    <p className="scan-attack-type">{scan.attack_type}</p>
                                </div>
                                <span className={`badge badge-lg ${
                                    scan.status === 'completed' ? 'badge-success' :
                                    scan.status === 'running' ? 'badge-info' :
                                    'badge-neutral'}`}
                                >
                                    {scan.status.charAt(0).toUpperCase() + scan.status.slice(1)}
                                </span>
                            </div>
                        </div>

                        <div className="card-body scan-body">
                            {scan.status === 'completed' && (
                                <div className="ai-analysis-box">
                                    <h3 className="section-heading">AI Analysis Status</h3>
                                    <div>
                                        {scan.report ? (
                                            <span className="badge badge-success badge-lg">
                                                Analysis Complete
                                            </span>
                                        ) : (
                                            <div className="ai-pending-row">
                                                <span className="status-note">
                                                    Waiting for AI Analysis
                                                </span>
                                                <button
                                                    onClick={analyzeScan}
                                                    disabled={isAnalyzing}
                                                    className="btn btn-primary btn-sm"
                                                >
                                                    {isAnalyzing ? (
                                                        <span className="btn-loading">
                                                            <svg className="loading-spinner-sm" viewBox="0 0 24 24">
                                                                <circle className="spinner-circle"></circle>
                                                                <path className="spinner-path"></path>
                                                            </svg>
                                                            Analyzing...
                                                        </span>
                                                    ) : (
                                                        'Analyze with AI'
                                                    )}
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}

                            <div className="activity-table-section">
                                <h3 className="section-heading">Recent Activity</h3>

                                <div className="table-wrapper">
                                    <table className="data-table">
                                        <thead>
                                            <tr>
                                                <th>Timestamp</th>
                                                <th>Payload</th>
                                                <th>Response</th>
                                                <th>Result</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {logs.length > 0 ? (
                                                logs.slice(0, 10).map((log: any) => (
                                                    <tr key={log.id}>
                                                        <td>
                                                            {new Date(log.timestamp).toLocaleString()}
                                                        </td>
                                                        <td>
                                                            <div className="code-cell font-mono">
                                                                {log.payload.length > 50 ? `${log.payload.substring(0, 50)}...` : log.payload}
                                                            </div>
                                                        </td>
                                                        <td>
                                                            <div className="code-cell font-mono">
                                                                {log.response.length > 30 ? `${log.response.substring(0, 30)}...` : log.response}
                                                            </div>
                                                        </td>
                                                        <td>
                                                            <span className={`badge ${getStatusBadgeClass(log.result)}`}>
                                                                {log.result.includes('detection') ? 'Vulnerability Found' : log.result}
                                                            </span>
                                                        </td>
                                                    </tr>
                                                ))
                                            ) : (
                                                <tr>
                                                    <td colSpan={4} className="table-empty">
                                                        No logs yet
                                                    </td>
                                                </tr>
                                            )}
                                        </tbody>
                                    </table>
                                </div>

                                {logs.length > 10 && (
                                    <div className="table-more-logs">
                                        <a href="#" className="link-more">
                                            View {logs.length - 10} more logs
                                        </a>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default ScanResults
