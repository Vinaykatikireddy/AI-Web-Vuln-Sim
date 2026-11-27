import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { errorHandler } from '../utils/errorHandler';

const API_BASE_URL = import.meta.env.VITE_AWVS_BASE_URL;

const FOCUS_OPTIONS = [
  { value: '', label: 'Autonomous Full Audit (Recommended)' },
  { value: 'Authentication, login, and session handling', label: 'Authentication & Session' },
  { value: 'Input validation, SQL injection, and XSS', label: 'Input Validation & Injection' },
  { value: 'Access control and IDOR', label: 'Access Control / IDOR' },
  { value: 'File upload validation and storage', label: 'File Upload Handling' },
];

const Attacks: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [lab, setLab] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [focus, setFocus] = useState('');
  const [scanId, setScanId] = useState<number | null>(null);
  const [scanStatus, setScanStatus] = useState<string>('');
  const [steps, setSteps] = useState<any[]>([]);
  const [reportId, setReportId] = useState<number | null>(null);

  const [starting, setStarting] = useState(false);
  const [promptInput, setPromptInput] = useState('');
  const [interacting, setInteracting] = useState(false);
  const [generatingReport, setGeneratingReport] = useState(false);

  const pollRef = useRef<number | null>(null);

  const authHeaders = () => ({
    Authorization: `Bearer ${localStorage.getItem('auth')}`,
  });

  useEffect(() => {
    const fetchLab = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/labs/${id}`, {
          headers: authHeaders(),
        });
        setLab(response.data);
      } catch (err) {
        setError(errorHandler(err));
      } finally {
        setLoading(false);
      }
    };
    fetchLab();

    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
  }, [id]);

  const fetchSteps = async (activeScanId: number) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/scans/${activeScanId}/steps`, {
        headers: authHeaders(),
      });
      setScanStatus(response.data.status);
      setSteps(response.data.steps || []);
      setReportId(response.data.report_id ?? null);

      if (response.data.status === 'completed' || response.data.status === 'failed') {
        if (pollRef.current) {
          window.clearInterval(pollRef.current);
          pollRef.current = null;
        }
      }
    } catch (err) {
      setError(errorHandler(err));
      if (pollRef.current) {
        window.clearInterval(pollRef.current);
        pollRef.current = null;
      }
    }
  };

  const handleStartAI = async () => {
    setStarting(true);
    setError('');
    setSteps([]);
    setReportId(null);
    if (pollRef.current) {
      window.clearInterval(pollRef.current);
      pollRef.current = null;
    }

    try {
      const response = await axios.post(
        `${API_BASE_URL}/scans/ai/run`,
        {
          lab_id: Number(id),
          attack_type: 'ai_autonomous',
          focus: focus || null,
        },
        { headers: authHeaders() }
      );
      const newScanId = response.data.id;
      setScanId(newScanId);
      setScanStatus(response.data.status);

      await fetchSteps(newScanId);
      pollRef.current = window.setInterval(() => fetchSteps(newScanId), 1500);
    } catch (err) {
      setError(errorHandler(err));
    } finally {
      setStarting(false);
    }
  };

  const handleInteract = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!scanId || !promptInput.trim()) return;
    setInteracting(true);
    setError('');
    try {
      const response = await axios.post(
        `${API_BASE_URL}/scans/${scanId}/interact`,
        { message: promptInput.trim() },
        { headers: authHeaders() }
      );
      setSteps(response.data.steps || []);
      setScanStatus(response.data.status);
      setPromptInput('');
    } catch (err) {
      setError(errorHandler(err));
    } finally {
      setInteracting(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!scanId) return;
    if (reportId) {
      navigate(`/report/${reportId}`);
      return;
    }
    setGeneratingReport(true);
    setError('');
    try {
      const response = await axios.post(
        `${API_BASE_URL}/scans/${scanId}/report`,
        {},
        { headers: authHeaders() }
      );
      navigate(`/report/${response.data.report_id}`);
    } catch (err) {
      setError(errorHandler(err));
    } finally {
      setGeneratingReport(false);
    }
  };

  if (loading) {
    return (
      <div className="page-loading">
        <div className="loading-spinner-wrap">
          <svg className="loading-spinner" viewBox="0 0 24 24">
            <circle className="spinner-circle"></circle>
            <path className="spinner-path"></path>
          </svg>
          <p className="loading-text">Loading AI Security Analyst...</p>
        </div>
      </div>
    );
  }

  const findingsCount = steps.filter((s) => s.role === 'finding').length;
  const isRunning = scanStatus === 'pending' || scanStatus === 'running';

  return (
    <div className="attacks-page">
      <div className="attacks-container">
        <div className="page-header-row">
          <div>
            <h1 className="page-title">AI Security Analyst — {lab?.name || `Lab ${id}`}</h1>
            <p className="page-subtitle" style={{ marginBottom: 0 }}>
              Autonomous LLM-driven reconnaissance, hypothesis testing, and proof-of-concept verification.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            {lab?.external_url && (
              <a
                href={lab.external_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-outline btn-sm"
              >
                Explore Target Site ↗
              </a>
            )}
            <button onClick={() => navigate(`/lab/${id}`)} className="btn btn-outline btn-sm">
              Back to Lab
            </button>
          </div>
        </div>

        {error && (
          <div className="alert alert-error" style={{ marginBottom: '1.25rem' }}>
            <div className="alert-content">
              <strong className="alert-title">Error: </strong>
              <span className="alert-message">{error}</span>
            </div>
          </div>
        )}

        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <div className="card-body" style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'flex-end', justifyContent: 'space-between' }}>
            <div style={{ flex: '1 1 280px' }}>
              <label className="info-label" htmlFor="ai-focus-select" style={{ display: 'block', marginBottom: '0.4rem' }}>
                Analysis Scope
              </label>
              <select
                id="ai-focus-select"
                className="form-input"
                value={focus}
                onChange={(e) => setFocus(e.target.value)}
                disabled={isRunning || starting}
              >
                {FOCUS_OPTIONS.map((opt) => (
                  <option key={opt.label} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
              <button
                onClick={handleStartAI}
                disabled={starting || isRunning}
                className="btn btn-primary"
              >
                {starting || isRunning ? 'AI Analyzing...' : scanId ? 'Re-run AI Attack' : 'Start AI Attack'}
              </button>

              {scanId && !isRunning && (
                <button
                  onClick={handleGenerateReport}
                  disabled={generatingReport}
                  className="btn btn-success"
                >
                  {generatingReport
                    ? 'Generating Report...'
                    : reportId
                    ? 'View Structured Report'
                    : 'Generate Structured Report'}
                </button>
              )}
            </div>
          </div>
        </div>

        {scanId && (
          <div className="card">
            <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 className="card-title">
                Live Agent Trace (Scan #{scanId})
              </h2>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <span className={`badge ${findingsCount > 0 ? 'badge-danger' : 'badge-neutral'}`}>
                  {findingsCount} Finding{findingsCount === 1 ? '' : 's'}
                </span>
                <span className={`badge ${scanStatus === 'completed' ? 'badge-success' : scanStatus === 'failed' ? 'badge-danger' : 'badge-warning'}`}>
                  {scanStatus}
                </span>
              </div>
            </div>

            <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {steps.length === 0 && (
                <p className="info-text">Initializing reconnaissance against {lab?.external_url}...</p>
              )}

              {steps.map((step) => {
                const isFinding = step.role === 'finding';
                const isUser = step.role === 'user';
                return (
                  <div
                    key={step.id}
                    style={{
                      padding: '0.9rem 1rem',
                      borderRadius: '0.5rem',
                      border: isFinding
                        ? '1px solid rgba(239, 68, 68, 0.45)'
                        : isUser
                        ? '1px solid rgba(59, 130, 246, 0.45)'
                        : '1px solid var(--border-color)',
                      background: isFinding
                        ? 'rgba(239, 68, 68, 0.08)'
                        : isUser
                        ? 'rgba(59, 130, 246, 0.08)'
                        : 'rgba(255, 255, 255, 0.02)',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <strong style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        Step {step.step_number} · {step.phase} {step.action_name ? `(${step.action_name})` : ''}
                      </strong>
                      {isFinding && step.action_input?.severity && (
                        <span className="badge badge-danger">{step.action_input.severity}</span>
                      )}
                      {step.log_id && (
                        <span className="badge badge-neutral">Log #{step.log_id}</span>
                      )}
                    </div>

                    {step.thought && (
                      <p className="info-text" style={{ marginBottom: '0.4rem' }}>{step.thought}</p>
                    )}

                    {isFinding && step.action_input && (
                      <div style={{ fontSize: '0.875rem', marginTop: '0.4rem' }}>
                        <p><strong>{step.action_input.title}</strong> ({step.action_input.endpoint})</p>
                        <p style={{ marginTop: '0.25rem' }}>{step.action_input.poc_summary}</p>
                        {step.action_input.remediation && (
                          <p style={{ marginTop: '0.25rem', color: '#34d399' }}>
                            <strong>Remediation:</strong> {step.action_input.remediation}
                          </p>
                        )}
                      </div>
                    )}

                    {!isFinding && step.action_name === 'send_request' && step.action_input && (
                      <pre className="code-block" style={{ marginTop: '0.4rem', fontSize: '0.8rem' }}>
                        <code>{`${step.action_input.method} ${step.action_input.path}${step.action_input.params ? ` ? ${JSON.stringify(step.action_input.params)}` : ''}${step.action_input.data ? ` | body=${JSON.stringify(step.action_input.data)}` : ''}`}</code>
                      </pre>
                    )}
                  </div>
                );
              })}

              {!isRunning && (
                <form onSubmit={handleInteract} style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="Ask the AI to explain a finding or test a specific endpoint/input..."
                    value={promptInput}
                    onChange={(e) => setPromptInput(e.target.value)}
                    disabled={interacting}
                    style={{ flex: 1 }}
                  />
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={interacting || !promptInput.trim()}
                  >
                    {interacting ? 'Sending...' : 'Ask / Steer AI'}
                  </button>
                </form>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Attacks;
