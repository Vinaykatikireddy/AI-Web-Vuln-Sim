import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { errorHandler } from '../utils/errorHandler'
import { updateAISettings, clearAllData } from '../api/settings'

const Settings: React.FC = () => {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
  const [settings, setSettings] = useState<any>({
    notifications: true,
    email_notifications: true,
    dark_mode: false,
    ai_analytics: true,
    auto_generate_reports: true,
    ai_endpoint: `${API_BASE_URL}/ai/analyze`,
    ai_api_key: ''
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/settings`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth')}`
          }
        })
        setSettings(response.data)
       } catch (err: any) {
         setError(errorHandler(err));
       } finally {
         setLoading(false)
       }
    }

    fetchSettings()
  }, [navigate])

    const handleUpdateSettings = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    try {
      const response = await axios.put(`${API_BASE_URL}/api/settings`, settings, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth')}`
        }
      })
      setSettings(response.data)
      alert('Settings updated successfully!')
     } catch (err: any) {
       setError(errorHandler(err));
     } finally {
       setIsSaving(false)
     }
  }

  const handleUpdateAISettings = async () => {
    const aiEndpoint = (document.getElementById('ai_endpoint') as HTMLInputElement).value;
    const aiApiKey = (document.getElementById('ai_api_key') as HTMLInputElement).value;

    setIsSaving(true);
    try {
      await updateAISettings(aiEndpoint, aiApiKey);
      setSettings({ ...settings, ai_endpoint: aiEndpoint, ai_api_key: aiApiKey });
      alert('AI settings updated successfully!');
    } catch (err: any) {
      setError(errorHandler(err));
    } finally {
      setIsSaving(false);
    }
  }

  const handleClearAllData = async () => {
    if (!window.confirm("Are you sure you want to clear all data? This action cannot be undone.")) return;

    setIsSaving(true);
    try {
      await clearAllData();
      alert('All data cleared successfully!');
    } catch (err: any) {
      setError(errorHandler(err));
    } finally {
      setIsSaving(false);
    }
  }

  const handleCheckboxChange = (key: string) => {
    setSettings({...settings, [key]: !settings[key]})
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <svg className="animate-spin -ml-1 mr-3 h-12 w-12 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="mt-4 text-gray-600">Loading settings...</p>
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
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Settings</h1>

          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-5 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Notification Preferences</h2>
            </div>

            <form onSubmit={handleUpdateSettings} className="px-6 py-5">
              <div className="space-y-6">
                <div className="flex items-start">
                  <div className="flex items-center h-5">
                    <input
                      id="notifications"
                      name="notifications"
                      type="checkbox"
                      checked={settings.notifications}
                      onChange={() => handleCheckboxChange('notifications')}
                      className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                    />
                  </div>
                  <div className="ml-3">
                    <label htmlFor="notifications" className="text-sm font-medium text-gray-900">
                      Enable notifications
                    </label>
                    <p className="text-sm text-gray-500">
                      Receive notifications for scan completions and new vulnerabilities
                    </p>
                  </div>
                </div>

                <div className="flex items-start">
                  <div className="flex items-center h-5">
                    <input
                      id="email_notifications"
                      name="email_notifications"
                      type="checkbox"
                      checked={settings.email_notifications}
                      onChange={() => handleCheckboxChange('email_notifications')}
                      className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                    />
                  </div>
                  <div className="ml-3">
                    <label htmlFor="email_notifications" className="text-sm font-medium text-gray-900">
                      Email notifications
                    </label>
                    <p className="text-sm text-gray-500">
                      Receive email notifications when scans complete or new vulnerabilities are detected
                    </p>
                  </div>
                </div>

                <div className="flex items-start">
                  <div className="flex items-center h-5">
                    <input
                      id="dark_mode"
                      name="dark_mode"
                      type="checkbox"
                      checked={settings.dark_mode}
                      onChange={() => handleCheckboxChange('dark_mode')}
                      className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                    />
                  </div>
                  <div className="ml-3">
                    <label htmlFor="dark_mode" className="text-sm font-medium text-gray-900">
                      Dark mode
                    </label>
                    <p className="text-sm text-gray-500">
                      Enable dark mode interface for better low-light readability
                    </p>
                  </div>
                </div>

                <div className="flex items-start">
                  <div className="flex items-center h-5">
                    <input
                      id="ai_analytics"
                      name="ai_analytics"
                      type="checkbox"
                      checked={settings.ai_analytics}
                      onChange={() => handleCheckboxChange('ai_analytics')}
                      className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                    />
                  </div>
                  <div className="ml-3">
                    <label htmlFor="ai_analytics" className="text-sm font-medium text-gray-900">
                      AI analytics
                    </label>
                    <p className="text-sm text-gray-500">
                      Enable advanced AI-powered vulnerability analysis and recommendations
                    </p>
                  </div>
                </div>

                <div className="flex items-start">
                  <div className="flex items-center h-5">
                    <input
                      id="auto_generate_reports"
                      name="auto_generate_reports"
                      type="checkbox"
                      checked={settings.auto_generate_reports}
                      onChange={() => handleCheckboxChange('auto_generate_reports')}
                      className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                    />
                  </div>
                  <div className="ml-3">
                    <label htmlFor="auto_generate_reports" className="text-sm font-medium text-gray-900">
                      Auto-generate reports
                    </label>
                    <p className="text-sm text-gray-500">
                      Automatically generate comprehensive reports after each scan completes
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  type="submit"
                  disabled={isSaving}
                  className="bg-blue-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                >
                  {isSaving ? (
                    <span className="flex items-center">
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Saving...
                    </span>
                  ) : (
                    'Save Changes'
                  )}
                </button>
              </div>
            </form>

            <div className="px-6 py-5 border-t border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Advanced Settings</h2>

              <div className="grid grid-cols-1 gap-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">API Settings</h3>
                  <p className="text-gray-600 mb-4">Configure the AI analysis engine</p>

                   <div className="space-y-4">
                     <div>
                       <label htmlFor="ai_endpoint" className="block text-sm font-medium text-gray-700">
                         AI Endpoint URL
                       </label>
                        <input
                          type="text"
                          id="ai_endpoint"
                          defaultValue={settings.ai_endpoint}
                          className="mt-1 block w-full shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm border-gray-300 rounded-md"
                        />
                     </div>

                     <div>
                       <label htmlFor="ai_api_key" className="block text-sm font-medium text-gray-700">
                         AI API Key
                       </label>
                       <input
                         type="password"
                         id="ai_api_key"
                         defaultValue={settings.ai_api_key}
                         className="mt-1 block w-full shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm border-gray-300 rounded-md"
                       />
                     </div>

                     <button
                         onClick={handleUpdateAISettings}
                         disabled={isSaving}
                         className="bg-blue-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                     >
                         {isSaving ? 'Saving...' : 'Save AI Settings'}
                     </button>
                   </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Data Retention</h3>
                  <p className="text-gray-600 mb-4">Control how long your scan data is stored</p>

                  <div className="space-y-4">
                    <div>
                      <label htmlFor="data_retention" className="block text-sm font-medium text-gray-700">
                        Retention Period
                      </label>
                      <select
                        id="data_retention"
                        defaultValue="90"
                        className="mt-1 block w-full shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm border-gray-300 rounded-md"
                      >
                        <option value="30">30 days</option>
                        <option value="90">90 days</option>
                        <option value="180">180 days</option>
                        <option value="365">1 year</option>
                        <option value="-1">Indefinitely</option>
                      </select>
                    </div>

                     <button
                         onClick={handleClearAllData}
                         disabled={isSaving}
                         className="bg-red-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50"
                     >
                         {isSaving ? 'Processing...' : 'Clear All Data'}
                     </button>
                  </div>
                </div>
              </div>
            </div>

            <div className="px-6 py-5 border-t border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">About</h2>

              <div className="space-y-4">
                <p className="text-gray-700">
                  <strong>Application:</strong> AI-Powered Web Application Attack Simulation Platform
                </p>
                <p className="text-gray-700">
                  <strong>Version:</strong> 0.1.0
                </p>
                <p className="text-gray-700">
                  <strong>Build Date:</strong> {new Date().toLocaleDateString()}
                </p>
                <p className="text-gray-700">
                  <strong>License:</strong> Educational Use Only
                </p>

                <div className="pt-4">
                  <p className="text-gray-700 mb-4">
                    This platform is designed for educational purposes only. All attacks are performed in isolated environments.
                  </p>
                  <p className="text-gray-700 mb-4">
                    © {new Date().getFullYear()} AI-Powered Attack Simulation Platform. All rights reserved.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings