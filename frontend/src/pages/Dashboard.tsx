import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { errorHandler } from '../utils/errorHandler'

const Dashboard: React.FC = () => {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
    const [dashboardData, setDashboardData] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/api/dashboard`, {
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
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <svg className="animate-spin -ml-1 mr-3 h-12 w-12 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <p className="mt-4 text-gray-600">Loading dashboard...</p>
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

    if (!dashboardData) return null

    return (
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
                <div className="border-4 border-dashed border-gray-200 rounded-lg h-full">
                    <h1 className="text-3xl font-bold text-gray-900 mb-6">Welcome back, {dashboardData.username}!</h1>

                    {/* Metrics Cards */}
                    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0 bg-blue-500 rounded-md p-3">
                                    <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                    </svg>
                                </div>
                                <div className="ml-5">
                                    <p className="text-sm font-medium text-gray-600">Total Scans</p>
                                    <p className="text-2xl font-semibold text-gray-900">{dashboardData.total_scans}</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                                    <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                    </svg>
                                </div>
                                <div className="ml-5">
                                    <p className="text-sm font-medium text-gray-600">Completed</p>
                                    <p className="text-2xl font-semibold text-gray-900">{dashboardData.completed_scans}</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0 bg-purple-500 rounded-md p-3">
                                    <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                                    </svg>
                                </div>
                                <div className="ml-5">
                                    <p className="text-sm font-medium text-gray-600">Active Labs</p>
                                    <p className="text-2xl font-semibold text-gray-900">{dashboardData.active_labs}</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0 bg-indigo-500 rounded-md p-3">
                                    <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                </div>
                                <div className="ml-5">
                                    <p className="text-sm font-medium text-gray-600">AI Reports</p>
                                    <p className="text-2xl font-semibold text-gray-900">{dashboardData.recent_reports.length}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Recent Scans */}
                    <div className="bg-white rounded-lg shadow mb-8">
                        <div className="px-4 py-5 sm:px-6">
                            <h2 className="text-lg font-medium text-gray-900">Recent Scans</h2>
                        </div>
                        <div className="border-t border-gray-200">
                            <ul className="divide-y divide-gray-200">
                                {dashboardData.recent_scans.length > 0 ? (
                                    dashboardData.recent_scans.map((scan: any) => (
                                        <li key={scan.id} className="px-4 py-4 sm:px-6">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center">
                                                    <div className="flex-shrink-0 h-10 w-10">
                                                        <div className="bg-blue-100 rounded-md flex items-center justify-center h-10 w-10">
                                                            <span className="text-blue-600 font-medium text-sm">
                                                                {scan.lab_name.charAt(0)}
                                                            </span>
                                                        </div>
                                                    </div>
                                                    <div className="ml-4">
                                                        <p className="text-sm font-medium text-gray-900">{scan.lab_name}</p>
                                                        <p className="text-sm text-gray-500">{scan.attack_type}</p>
                                                    </div>
                                                </div>
                                                <div className="ml-4 flex items-center">
                                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${scan.status === 'generated' ? 'bg-green-100 text-green-800' : scan.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                                                    </span>
                                                    <Link
                                                        to={`/scan/${scan.id}`}
                                                        className="ml-4 text-sm text-blue-600 hover:text-blue-500"
                                                    >
                                                        View
                                                    </Link>
                                                </div>
                                            </div>
                                        </li>
                                    ))
                                ) : (
                                    <li className="px-4 py-4 sm:px-6 text-center text-gray-500">
                                        No recent scans
                                    </li>
                                )}
                            </ul>
                        </div>
                        <div className="px-4 py-4 sm:px-6 border-t border-gray-200">
                            <Link to="/labs" className="text-sm font-medium text-blue-600 hover:text-blue-500">
                                View all labs →
                            </Link>
                        </div>
                    </div>

                    {/* Recent Reports */}
                    <div className="bg-white rounded-lg shadow">
                        <div className="px-4 py-5 sm:px-6">
                            <h2 className="text-lg font-medium text-gray-900">Recent AI Reports</h2>
                        </div>
                        <div className="border-t border-gray-200">
                            <ul className="divide-y divide-gray-200">
                                {dashboardData.recent_reports.length > 0 ? (
                                    dashboardData.recent_reports.map((report: any) => (
                                        <li key={report.id} className="px-4 py-4 sm:px-6">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center">
                                                    <div className="flex-shrink-0 h-10 w-10">
                                                        <div className="bg-indigo-100 rounded-md flex items-center justify-center h-10 w-10">
                                                            <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                            </svg>
                                                        </div>
                                                    </div>
                                                    <div className="ml-4">
                                                        <p className="text-sm font-medium text-gray-900">Scan #{report.scan_id}</p>
                                                        <p className="text-sm text-gray-500">Generated {new Date(report.generated_at).toLocaleDateString()}</p>
                                                    </div>
                                                </div>
                                                <div className="ml-4 flex items-center">
                                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${report.status === 'generated' ? 'bg-green-100 text-green-800' : report.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                                                    </span>
                                                    <Link
                                                        to={`/report/${report.id}`}
                                                        className="ml-4 text-sm text-blue-600 hover:text-blue-500"
                                                    >
                                                        View
                                                    </Link>
                                                </div>
                                            </div>
                                        </li>
                                    ))
                                ) : (
                                    <li className="px-4 py-4 sm:px-6 text-center text-gray-500">
                                        No recent reports
                                    </li>
                                )}
                            </ul>
                        </div>
                        <div className="px-4 py-4 sm:px-6 border-t border-gray-200">
                            <Link to="/scans/history" className="text-sm font-medium text-blue-600 hover:text-blue-500">
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