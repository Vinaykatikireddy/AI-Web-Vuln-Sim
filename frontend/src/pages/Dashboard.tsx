import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { errorHandler } from '../utils/errorHandler'

const Dashboard: React.FC = () => {
    const API_BASE_URL = import.meta.env.VITE_AWVS_BASE_URL;
    const [dashboardData, setDashboardData] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/dashboard`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('auth')}`
                    }
                })
                setDashboardData(response.data)
            } catch (err: any) {
                setError(errorHandler(err));
            } finally {
                setLoading(false)
            }
        }

        fetchDashboardData()
    }, [])

    if (loading) {
        return (
            <div className="page-loading">
                <div className="loading-spinner-wrap">
                    <svg className="loading-spinner" viewBox="0 0 24 24">
                        <circle className="spinner-circle"></circle>
                        <path className="spinner-path"></path>
                    </svg>
                    <p className="loading-text">Loading dashboard...</p>
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

    if (!dashboardData) return null

    return (
        <div className="dashboard-page">
            <div className="dashboard-container">
                <div className="dashboard-content">
                    <h1 className="page-title">Welcome back, {dashboardData.username}!</h1>

                    {/* Metrics Cards */}
                    <div className="stats-grid">
                        <div className="stat-card">
                            <div className="stat-card-inner">
                                <div className="stat-icon-wrap bg-blue-subtle">
                                    <svg className="stat-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                    </svg>
                                </div>
                                <div className="stat-info">
                                    <p className="stat-label">Total Scans</p>
                                    <p className="stat-value">{dashboardData.total_scans}</p>
                                </div>
                            </div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-card-inner">
                                <div className="stat-icon-wrap bg-blue-subtle">
                                    <svg className="stat-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                    </svg>
                                </div>
                                <div className="stat-info">
                                    <p className="stat-label">Completed</p>
                                    <p className="stat-value">{dashboardData.completed_scans}</p>
                                </div>
                            </div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-card-inner">
                                <div className="stat-icon-wrap bg-blue-subtle">
                                    <svg className="stat-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                                    </svg>
                                </div>
                                <div className="stat-info">
                                    <p className="stat-label">Active Labs</p>
                                    <p className="stat-value">{dashboardData.active_labs}</p>
                                </div>
                            </div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-card-inner">
                                <div className="stat-icon-wrap bg-blue-subtle">
                                    <svg className="stat-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                </div>
                                <div className="stat-info">
                                    <p className="stat-label">AI Reports</p>
                                    <p className="stat-value">{dashboardData.recent_reports.length}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Recent Scans */}
                    <div className="card dashboard-section">
                        <div className="card-header">
                            <h2 className="card-title">Recent Scans</h2>
                        </div>
                        <div className="card-body" style={{ padding: 0 }}>
                            <ul className="activity-list">
                                {dashboardData.recent_scans.length > 0 ? (
                                    dashboardData.recent_scans.map((scan: any) => (
                                        <li key={scan.id} className="activity-item">
                                            <div className="activity-item-inner">
                                                <div className="activity-main">
                                                    <div className="activity-avatar-wrap">
                                                        <div className="activity-avatar">
                                                            <span className="avatar-initial">
                                                                {scan.lab_name.charAt(0)}
                                                            </span>
                                                        </div>
                                                    </div>
                                                    <div className="activity-details">
                                                        <p className="activity-title">{scan.lab_name}</p>
                                                        <p className="activity-subtitle">{scan.attack_type}</p>
                                                    </div>
                                                </div>
                                                <div className="activity-actions">
                                                    <span className={`badge ${scan.status === 'generated' || scan.status === 'completed' ? 'badge-success' : scan.status === 'pending' ? 'badge-warning' : 'badge-danger'}`}>
                                                        {scan.status}
                                                    </span>
                                                    <Link
                                                        to={`/scan/${scan.id}`}
                                                        className="btn btn-sm btn-outline"
                                                    >
                                                        View
                                                    </Link>
                                                </div>
                                            </div>
                                        </li>
                                    ))
                                ) : (
                                    <li className="activity-empty">
                                        No recent scans
                                    </li>
                                )}
                            </ul>
                        </div>
                        <div className="card-footer">
                            <Link to="/labs" className="link-arrow">
                                View all labs →
                            </Link>
                        </div>
                    </div>

                    {/* Recent Reports */}
                    <div className="card dashboard-section">
                        <div className="card-header">
                            <h2 className="card-title">Recent AI Reports</h2>
                        </div>
                        <div className="card-body" style={{ padding: 0 }}>
                            <ul className="activity-list">
                                {dashboardData.recent_reports.length > 0 ? (
                                    dashboardData.recent_reports.map((report: any) => (
                                        <li key={report.id} className="activity-item">
                                            <div className="activity-item-inner">
                                                <div className="activity-main">
                                                    <div className="activity-avatar-wrap">
                                                        <div className="activity-icon-badge">
                                                            <svg className="report-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                            </svg>
                                                        </div>
                                                    </div>
                                                    <div className="activity-details">
                                                        <p className="activity-title">Scan #{report.scan_id}</p>
                                                        <p className="activity-subtitle">Generated {new Date(report.generated_at).toLocaleDateString()}</p>
                                                    </div>
                                                </div>
                                                <div className="activity-actions">
                                                    <span className={`badge ${report.status === 'generated' ? 'badge-success' : report.status === 'pending' ? 'badge-warning' : 'badge-danger'}`}>
                                                        {report.status}
                                                    </span>
                                                    <Link
                                                        to={`/report/${report.id}`}
                                                        className="btn btn-sm btn-outline"
                                                    >
                                                        View
                                                    </Link>
                                                </div>
                                            </div>
                                        </li>
                                    ))
                                ) : (
                                    <li className="activity-empty">
                                        No recent reports
                                    </li>
                                )}
                            </ul>
                        </div>
                        <div className="card-footer">
                            <Link to="/scans/history" className="link-arrow">
                                View all reports →
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Dashboard
