import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import axios from 'axios'
import { errorHandler } from '../utils/errorHandler'

const LabDetails: React.FC = () => {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const [lab, setLab] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [isStarting, setIsStarting] = useState(false)
    const [isStopping, setIsStopping] = useState(false)

    useEffect(() => {
        const fetchLab = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/api/labs/${id}`, {
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

    const handleStartLab = async () => {
        setIsStarting(true)
        try {
            await axios.post(`${API_BASE_URL}/api/labs/start`, { lab_id: parseInt(id!) }, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth')}`
                }
            })
            // Refresh lab details
            const response = await axios.get(`${API_BASE_URL}/api/labs/${id}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth')}`
                }
            })
            setLab(response.data)
        } catch (err: any) {
            setError(errorHandler(err));
        } finally {
            setIsStarting(false)
        }
    }

    const handleStopLab = async () => {
        setIsStopping(true)
        try {
            await axios.post(`${API_BASE_URL}/api/labs/stop`, { lab_id: parseInt(id!) }, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth')}`
                }
            })
            // Refresh lab details
            const response = await axios.get(`${API_BASE_URL}/api/labs/${id}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth')}`
                }
            })
            setLab(response.data)
        } catch (err: any) {
            setError(errorHandler(err));
        } finally {
            setIsStopping(false)
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
                    <p className="mt-4 text-gray-600">Loading lab details...</p>
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
                        Back to Labs
                    </button>
                </div>
            </div>
        )
    }

    if (!lab) return null

    const vulnerabilityIcons: Record<string, JSX.Element> = {
        'SQL Injection': <svg className="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>,
        'XSS': <svg className="h-5 w-5 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>,
        'IDOR': <svg className="h-5 w-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>,
        'File Upload': <svg className="h-5 w-5 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
    }

    const vulnerabilityMap: Record<string, string[]> = {
        'Simple Login': ['SQL Injection'],
        'Blog': ['XSS'],
        'Ecommerce': ['IDOR'],
        'File Upload': ['File Upload']
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
                        <h1 className="text-3xl font-bold text-gray-900">{lab.name}</h1>
                    </div>

                    <div className="bg-white rounded-lg shadow overflow-hidden">
                        <div className="px-6 py-5 border-b border-gray-200">
                            <div className="flex items-start justify-between">
                                <div>
                                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium
${lab.status === 'running' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}
                                    >
                                        {lab.status.charAt(0).toUpperCase() + lab.status.slice(1)}
                                    </span>
                                    <p className="mt-1 text-sm text-gray-600">{lab.description || 'No description available'}</p>
                                </div>

                                <div className="flex space-x-2">
                                    {lab.status === 'stopped' ? (
                                        <button
                                            onClick={handleStartLab}
                                            disabled={isStarting}
                                            className="bg-blue-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                                        >
                                            {isStarting ? (
                                                <span className="flex items-center">
                                                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                                    </svg>
                                                    Starting...
                                                </span>
                                            ) : (
                                                'Start Lab'
                                            )}
                                        </button>
                                    ) : (
                                        <button
                                            onClick={handleStopLab}
                                            disabled={isStopping}
                                            className="bg-red-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50"
                                        >
                                            {isStopping ? (
                                                <span className="flex items-center">
                                                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                                    </svg>
                                                    Stopping...
                                                </span>
                                            ) : (
                                                'Stop Lab'
                                            )}
                                        </button>
                                    )}

                                    <Link
                                        to={`/lab/${lab.id}/attacks`}
                                        className="bg-gray-100 text-gray-700 py-2 px-4 rounded-md text-sm font-medium hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                                    >
                                        Run Attack
                                    </Link>
                                </div>
                            </div>

                            <div className="mt-4">
                                <h3 className="text-sm font-semibold text-gray-900 mb-2">Vulnerabilities</h3>
                                <div className="flex flex-wrap gap-2">
                                    {vulnerabilityMap[lab.name]!.map((vuln) => (
                                        <span key={vuln} className="flex items-center bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs font-medium">
                                            {vulnerabilityIcons[vuln]}
                                            <span className="ml-1">{vuln}</span>
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className="px-6 py-5">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Lab Details</h3>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <h4 className="text-sm font-medium text-gray-700 mb-2">Docker Image</h4>
                                    <p className="text-gray-900">{lab.docker_image}</p>
                                </div>

                                <div>
                                    <h4 className="text-sm font-medium text-gray-700 mb-2">Port</h4>
                                    <p className="text-gray-900">{lab.port || 'N/A'}</p>
                                </div>
                            </div>

                            <div className="mt-6">
                                <h4 className="text-sm font-medium text-gray-700 mb-2">Description</h4>
                                <p className="text-gray-900">{lab.description || 'No detailed description available for this lab.'}</p>
                            </div>

                            <div className="mt-6">
                                <h4 className="text-sm font-medium text-gray-700 mb-2">Security Note</h4>
                                <p className="text-gray-900">This lab is purposefully vulnerable to help you learn cybersecurity practices. Only use it for educational purposes within this platform.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default LabDetails