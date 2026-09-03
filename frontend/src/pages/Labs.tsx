import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { errorHandler } from '../utils/errorHandler'

const Labs: React.FC = () => {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
    const [labs, setLabs] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    useEffect(() => {
        const fetchLabs = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/api/labs`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('auth')}`
                    }
                })
                setLabs(response.data)
            } catch (err: any) {
                setError(errorHandler(err));
            } finally {
                setLoading(false)
            }
        }

        fetchLabs()
    }, [])

    const handleStartLab = async (labId: number) => {
        try {
            await axios.post(`${API_BASE_URL}/api/labs/start`, { lab_id: labId }, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth')}`
                }
            })
            // Refresh labs list
            const response = await axios.get(`${API_BASE_URL}/api/labs`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth')}`
                }
            })
            setLabs(response.data)
        } catch (err: any) {
            setError(errorHandler(err));
        }
    }

    const handleStopLab = async (labId: number) => {
        try {
            await axios.post(`${API_BASE_URL}/api/labs/stop`, { lab_id: labId }, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth')}`
                }
            })
            // Refresh labs list
            const response = await axios.get(`${API_BASE_URL}/api/labs`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth')}`
                }
            })
            setLabs(response.data)
        } catch (err: any) {
            setError(errorHandler(err));
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
                    <p className="mt-4 text-gray-600">Loading labs...</p>
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

    return (
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
                <div className="border-4 border-dashed border-gray-200 rounded-lg h-full">
                    <h1 className="text-3xl font-bold text-gray-900 mb-6">Vulnerable Labs</h1>

                    <p className="text-lg text-gray-600 mb-8">
                        Select a lab to start a secure, simulated attack environment.
                    </p>

                    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
                        {labs.map((lab: any) => (
                            <div key={lab.id} className="bg-white rounded-lg shadow overflow-hidden">
                                <div className="p-6">
                                    <h3 className="text-xl font-semibold text-gray-900 mb-2">{lab.name}</h3>
                                    <p className="text-gray-600 mb-4">{lab.description || 'No description available'}</p>

                                    {lab.status === 'error' && (
                                        <div className="flex items-center mb-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${lab.status === 'running' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                {lab.status.charAt(0).toUpperCase() + lab.status.slice(1)}
                                            </span>
                                        </div>
                                    )}

                                    <div className="flex space-x-2">
                                        {lab.status === 'error' ? (
                                            <button
                                                    className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 cursor-not-allowed"
                                                >
                                                    Lab Broken
                                                </button>
                                        ) : lab.status === 'stopped' ? (
                                                <button
                                                    onClick={() => handleStartLab(lab.id)}
                                                    className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                                                >
                                                    Start Lab
                                                </button>
                                            ) : (
                                                <button
                                                    onClick={() => handleStopLab(lab.id)}
                                                    className="flex-1 bg-red-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                                                >
                                                    Stop Lab
                                                </button>
                                            )
                                        }
                                        <Link
                                            to={`/lab/${lab.id}`}
                                            className="bg-gray-100 text-gray-700 py-2 px-4 rounded-md text-sm font-medium hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                                        >
                                            Details
                                        </Link>
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