import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { errorHandler } from '../utils/errorHandler'

const ScanResults: React.FC = () => {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
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
                const response = await axios.get(`${API_BASE_URL}/api/scans/${id}`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('auth')}`
                    }
                })
                setScan(response.data)

                // Fetch logs
                const logsResponse = await axios.get(`${API_BASE_URL}/api/logs?scan_id=${id}`, {
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
            await axios.post(`${API_BASE_URL}/api/ai/analyze`, { scan_id: parseInt(id!) }, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth')}`
                }
            })

            // Refresh scan data to show updated status
            const response = await axios.get(`${API_BASE_URL}/api/scans/${id}`, {
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
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <svg className="animate-spin -ml-1 mr-3 h-12 w-12 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <p className="mt-4 text-gray-600">Loading scan results...</p>
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
                        onClick={() => navigate(-1)}
                        className="mt-4 btn btn-primary"
                    >
                        Back to Dashboard
                    </button>
                </div>
            </div>
        )
    }

    if (!scan || !logs) return null

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'success': return 'bg-green-100 text-green-800'
            case 'failure': return 'bg-red-100 text-red-800'
            case 'vulnerability_detected': return 'bg-red-100 text-red-800'
            default: return 'bg-gray-100 text-gray-800'
        }
    }

    return (
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
                <div className="border-4 border-dashed border-gray-200 rounded-lg h-full">
                    <div className="flex items-center mb-6">
                        <button
                            onClick={() => navigate(-1)}
                            className="mr-4 text-blue-600 hover:text-blue-500"
                        >
                            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
                            </svg>
                        </button>
                        <h1 className="text-3xl font-bold text-gray-900">Scan Results</h1>
                    </div>

                    <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
                        <div className="px-6 py-5 border-b border-gray-200">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h2 className="text-xl font-semibold text-gray-900">{scan.lab.name}</h2>
                                    <p className="text-gray-600">{scan.attack_type}</p>
                                </div>
                                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium
${scan.status === 'completed' ? 'bg-green-100 text-green-800' :
                                        scan.status === 'running' ? 'bg-blue-100 text-blue-800' :
                                            'bg-gray-100 text-gray-800'}`}
                                >
                                    {scan.status.charAt(0).toUpperCase() + scan.status.slice(1)}
                                </span>
                            </div>
                        </div>

                        <div className="px-6 py-5">
                            {scan.status === 'completed' && (
                                <div className="mb-6">
                                    <h3 className="text-lg font-medium text-gray-900 mb-4">AI Analysis Status</h3>
                                    <div className="flex items-center space-x-4">
                                        {scan.report ? (
                                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                                                Analysis Complete
                                            </span>
                                        ) : (
                                            <div className="flex items-center">
                                                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                                                    Waiting for AI Analysis
                                                </span>
                                                <button
                                                    onClick={analyzeScan}
                                                    disabled={isAnalyzing}
                                                    className="ml-4 bg-blue-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                                                >
                                                    {isAnalyzing ? (
                                                        <span className="flex items-center">
                                                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
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

                            <div className="mt-6">
                                <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>

                                <div className="border border-gray-200 rounded-lg overflow-hidden">
                                    <table className="min-w-full divide-y divide-gray-200">
                                        <thead className="bg-gray-50">
                                            <tr>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Payload</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Response</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Result</th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white divide-y divide-gray-200">
                                            {logs.length > 0 ? (
                                                logs.slice(0, 10).map((log: any) => (
                                                    <tr key={log.id} className="hover:bg-gray-50">
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                            {new Date(log.timestamp).toLocaleString()}
                                                        </td>
                                                        <td className="px-6 py-4 whitespace-nowrap">
                                                            <div className="text-sm text-gray-900 font-mono bg-gray-100 px-2 py-1 rounded">
                                                                {log.payload.length > 50 ? `${log.payload.substring(0, 50)}...` : log.payload}
                                                            </div>
                                                        </td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                            {log.response.length > 30 ? `${log.response.substring(0, 30)}...` : log.response}
                                                        </td>
                                                        <td className="px-6 py-4 whitespace-nowrap">
                                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(log.result)}`}
                                                            >
                                                                {log.result.includes('detection') ? 'Vulnerability Found' : log.result}
                                                            </span>
                                                        </td>
                                                    </tr>
                                                ))
                                            ) : (
                                                <tr>
                                                    <td colSpan={4} className="px-6 py-4 text-center text-gray-500">
                                                        No logs yet
                                                    </td>
                                                </tr>
                                            )}
                                        </tbody>
                                    </table>
                                </div>

                                {logs.length > 10 && (
                                    <div className="mt-4 text-center">
                                        <a href="#" className="text-blue-600 hover:text-blue-500">
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