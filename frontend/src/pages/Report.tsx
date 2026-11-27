import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { errorHandler } from '../utils/errorHandler'

const Report: React.FC = () => {
  const API_BASE_URL = import.meta.env.VITE_AWVS_BASE_URL;
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
        const reportResponse = await axios.get(`${API_BASE_URL}/reports/${id}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth')}`
          }
        })
        setReport(reportResponse.data)

        const scanResponse = await axios.get(`${API_BASE_URL}/scans/${reportResponse.data.scan_id}`, {
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
      const response = await axios.get(`${API_BASE_URL}/reports/${id}?format=${downloadType}`, {
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
      <div className="page-loading">
        <div className="loading-spinner-wrap">
          <svg className="loading-spinner" viewBox="0 0 24 24">
            <circle className="spinner-circle"></circle>
            <path className="spinner-path"></path>
          </svg>
          <p className="loading-text">Loading report...</p>
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

  if (!report || !scan) return null

  const renderContent = () => {
    try {
      const content =
        typeof report.content === 'string' ? JSON.parse(report.content) : report.content

      return (
        <div className="report-document">
          <h1 className="doc-title">Security Assessment Report</h1>

          <div className="doc-section executive-summary">
            <h2 className="doc-section-title">Executive Summary</h2>
            <p className="doc-paragraph">
              {content.executive_summary ||
                `This report summarizes the security assessment of the ${scan.lab?.name || 'target'} application. The evaluation identified ${content.findings?.length || 0} security vulnerabilities with a risk score of ${content.risk_score ?? 0}.`}
            </p>
            <p className="doc-paragraph">
              Risk Score: <strong>{content.risk_score ?? 0}/100</strong> · Performed on{' '}
              {new Date(report.generated_at).toLocaleDateString()} using AI-powered analysis.
            </p>
          </div>

          <div className="doc-section">
            <h2 className="doc-section-title">Findings</h2>

            {(!content.findings || content.findings.length === 0) && (
              <p className="doc-paragraph">No verified vulnerabilities were recorded during this run.</p>
            )}

            {(content.findings || []).map((finding: any, index: number) => (
              <div key={index} className="finding-card">
                <div className="finding-header">
                  <div className="finding-title-group">
                    <h3 className="finding-title">{finding.title || finding.vulnerability_type}</h3>
                    <span className={`badge ${
                      finding.risk_level === 'critical' ? 'badge-critical' :
                      finding.risk_level === 'high' ? 'badge-high' :
                      finding.risk_level === 'medium' ? 'badge-medium' :
                      'badge-low'}`}
                    >
                      {finding.risk_level.charAt(0).toUpperCase() + finding.risk_level.slice(1)}
                    </span>
                  </div>
                  <div className="finding-severity">
                    <span>Severity: {finding.risk_level}</span>
                  </div>
                </div>

                <div className="finding-body">
                  <h4 className="finding-subheading">Technical Explanation</h4>
                  <p className="finding-text">{finding.technical_explanation}</p>

                  <h4 className="finding-subheading">Proof-of-Concept Evidence</h4>
                  <p className="finding-text">{finding.example_exploitation}</p>
                  {finding.poc_evidence && (
                    <pre className="code-block" style={{ marginBottom: '1rem' }}>
                      <code>{`Log #${finding.poc_evidence.log_id ?? 'N/A'}\nRequest: ${finding.poc_evidence.request}\nResponse:\n${finding.poc_evidence.response_excerpt}`}</code>
                    </pre>
                  )}

                  <h4 className="finding-subheading">Remediation &amp; Prevention</h4>
                  <p className="finding-text">{finding.prevention}</p>

                  <h4 className="finding-subheading">Secure Code Recommendation</h4>
                  <pre className="code-block">
                    <code>{finding.secure_code_recommendation}</code>
                  </pre>
                </div>
              </div>
            ))}
          </div>

          <div className="doc-section evidence-section">
            <h2 className="doc-section-title">Evidence</h2>

            {content.evidence && content.evidence.map((evidence: any, index: number) => (
              <div key={index} className="evidence-card">
                <h3 className="evidence-title">Evidence #{index + 1}</h3>
                <div className="evidence-details">
                  <p className="evidence-line"><strong>Payload:</strong> <code className="inline-code">{evidence.payload}</code></p>
                  <p className="evidence-line"><strong>Request:</strong> <code className="inline-code">{evidence.request}</code></p>
                  <p className="evidence-line"><strong>Response:</strong> <code className="inline-code">{evidence.response}</code></p>
                </div>
              </div>
            ))}
          </div>

          <div className="doc-section recommendations-section">
            <h2 className="doc-section-title">AI Recommendations</h2>
            <p className="doc-paragraph">{content.ai_recommendations}</p>

            {content.ongoing_recommendations && (
              <div className="ongoing-recommendations" style={{ marginTop: '0.75rem' }}>
                <h3 className="finding-subheading" style={{ marginBottom: '0.5rem' }}>Ongoing Recommendations</h3>
                <ul className="recommendations-list">
                  {content.ongoing_recommendations.map((rec: string, index: number) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="doc-section risk-score-section">
            <h2 className="doc-section-title">Risk Score</h2>
            <p className="doc-paragraph">The overall risk score for this assessment is: <strong style={{ color: 'var(--text-primary)' }}>{content.risk_score}/100</strong></p>

            <div className="risk-progress-track">
              <div
                className="risk-progress-bar"
                style={{ width: `${(content.risk_score / 100) * 100}%` }}
              ></div>
            </div>

            <p className="risk-level-alert">
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
        <div className="alert alert-error">
          <p>Failed to parse report content</p>
          <pre className="code-block" style={{ marginTop: '0.75rem' }}>
            {report.content}
          </pre>
        </div>
      )
    }
  }

  return (
    <div className="report-page">
      <div className="report-container">
        <div className="report-content">
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
              <h1 className="page-title">Security Report</h1>
            </div>
          </div>

          <div className="card report-card">
            <div className="card-header report-header-bar">
              <div className="report-header-inner">
                <div>
                  <h2 className="report-lab-title">Assessment of {scan.lab.name}</h2>
                  <p className="report-date-subtitle">Generated on {new Date(report.generated_at).toLocaleString()}</p>
                </div>
                <div className="report-download-controls">
                  <select
                    value={downloadType}
                    onChange={(e) => setDownloadType(e.target.value as any)}
                    className="form-select form-select-sm"
                  >
                    <option value="html">HTML</option>
                    <option value="markdown">Markdown</option>
                    <option value="pdf">PDF</option>
                  </select>
                  <button
                    onClick={downloadReport}
                    className="btn btn-sm btn-primary"
                  >
                    Download
                  </button>
                </div>
              </div>
            </div>

            <div className="card-body report-body">
              {renderContent()}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Report
