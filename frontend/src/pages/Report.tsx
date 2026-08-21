import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { errorHandler } from '../utils/errorHandler'

const Report: React.FC = () => {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [report, setReport] = useState<any>(null)
  const [scan, setScan] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [downloadType, setDownloadType] = useState<'html' | 'markdown' | 'pdf'>('html')

  useEffect(() => {
    const fetchReportData = async () => {
      try {
        const reportResponse = await axios.get(`${API_BASE_URL}/api/reports/${id}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth')}`
          }
        })
        setReport(reportResponse.data)

        const scanResponse = await axios.get(`${API_BASE_URL}/api/scans/${reportResponse.data.scan_id}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth')}`
          }
        })
        setScan(scanResponse.data)
       } catch (err: any) {
         setError(errorHandler(err));
       } finally {
         setLoading(false)
       }
    }

    fetchReportData()
  }, [id])

  const downloadReport = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/reports/${id}?format=${downloadType}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth')}`
        },
        responseType: 'blob'
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `report-${id}.${downloadType}`)
      document.body.appendChild(link)
      link.click()
      link.parentNode!.removeChild(link)
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
          <p className="mt-4 text-gray-600">Loading report...</p>
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

  if (!report || !scan) return null

  const renderContent = () => {
    try {
      const content = JSON.parse(report.content)

      return (
        <div className="prose max-w-none">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Security Assessment Report</h1>

          <div className="bg-gray-50 p-6 rounded-lg mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Executive Summary</h2>
            <p className="text-gray-700 mb-4">This report summarizes the security assessment of the {scan.lab.name} application. The evaluation identified {content.findings.length} security vulnerabilities with a risk score of {content.risk_score}.</p>
            <p className="text-gray-700">The assessment was performed on {new Date(report.generated_at).toLocaleDateString()} using AI-powered analysis.</p>
          </div>

          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Findings</h2>

          {content.findings.map((finding: any, index: number) => (
            <div key={index} className="bg-white rounded-lg shadow p-6 mb-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">{finding.vulnerability_type}</h3>
                  <div className="flex items-center mt-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                      ${finding.risk_level === 'critical' ? 'bg-red-100 text-red-800' :
                        finding.risk_level === 'high' ? 'bg-red-100 text-red-800' :
                        finding.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'}`}
                    >
                      {finding.risk_level.charAt(0).toUpperCase() + finding.risk_level.slice(1)}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-sm text-gray-500">Severity: {finding.risk_level}</span>
                </div>
              </div>

              <div className="prose max-w-none">
                <h4 className="text-lg font-medium text-gray-900 mb-2">Technical Explanation</h4>
                <p className="text-gray-700 mb-4">{finding.technical_explanation}</p>

                <h4 className="text-lg font-medium text-gray-900 mb-2">Example Exploitation</h4>
                <p className="text-gray-700 mb-4">{finding.example_exploitation}</p>

                <h4 className="text-lg font-medium text-gray-900 mb-2">Prevention</h4>
                <p className="text-gray-700 mb-4">{finding.prevention}</p>

                <h4 className="text-lg font-medium text-gray-900 mb-2">Secure Code Recommendation</h4>
                <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{finding.secure_code_recommendation}</code>
                </pre>
              </div>
            </div>
          ))}

          <div className="bg-gray-50 p-6 rounded-lg mt-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Evidence</h2>

            {content.evidence && content.evidence.map((evidence: any, index: number) => (
              <div key={index} className="mb-6">
                <h3 className="text-xl font-medium text-gray-900 mb-2">Evidence #{index + 1}</h3>
                <div className="bg-gray-100 p-4 rounded-lg">
                  <p className="text-gray-700 mb-2"><strong>Payload:</strong> {evidence.payload}</p>
                  <p className="text-gray-700 mb-2"><strong>Request:</strong> {evidence.request}</p>
                  <p className="text-gray-700"><strong>Response:</strong> {evidence.response}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-gray-50 p-6 rounded-lg mt-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">AI Recommendations</h2>
            <p className="text-gray-700 mb-4">{content.ai_recommendations}</p>

            {content.ongoing_recommendations && (
              <div className="mt-4">
                <h3 className="text-xl font-medium text-gray-900 mb-2">Ongoing Recommendations</h3>
                <ul className="list-disc list-inside text-gray-700">
                  {content.ongoing_recommendations.map((rec: string, index: number) => (
                    <li key={index} className="mb-2">{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="bg-gray-50 p-6 rounded-lg mt-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Risk Score</h2>
            <p className="text-gray-700 mb-4">The overall risk score for this assessment is: {content.risk_score}/100</p>

            <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
              <div
                className="bg-red-600 h-2.5 rounded-full"
                style={{ width: `${(content.risk_score / 100) * 100}%` }}
              ></div>
            </div>

            <p className="text-gray-700">
              {content.risk_score > 80 ? 'Critical: Immediate action required' :
                content.risk_score > 60 ? 'High: Action required soon' :
                content.risk_score > 40 ? 'Medium: Address in future updates' :
                'Low: Minimal risk'}
            </p>
          </div>
        </div>
      )
    } catch (e) {
      return (
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-700">Failed to parse report content</p>
          <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
            {report.content}
          </pre>
        </div>
      )
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
            <h1 className="text-3xl font-bold text-gray-900">Security Report</h1>
          </div>

          <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
            <div className="px-6 py-5 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Assessment of {scan.lab.name}</h2>
                  <p className="text-gray-600">Generated on {new Date(report.generated_at).toLocaleString()}</p>
                </div>
                <div className="flex space-x-3">
                  <select
                    value={downloadType}
                    onChange={(e) => setDownloadType(e.target.value as any)}
                    className="border border-gray-300 rounded-md px-3 py-2 text-sm"
                  >
                    <option value="html">HTML</option>
                    <option value="markdown">Markdown</option>
                    <option value="pdf">PDF</option>
                  </select>
                  <button
                    onClick={downloadReport}
                    className="bg-blue-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    Download
                  </button>
                </div>
              </div>
            </div>

            <div className="px-6 py-5">
              {renderContent()}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Report