import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { errorHandler } from '../utils/errorHandler';

const API_BASE_URL = import.meta.env.VITE_AWVS_BASE_URL;

const ScanHistory: React.FC = () => {
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchScans = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/scans/history`);
        setScans(response.data);
      } catch (err) {
        setError(errorHandler(err));
      } finally {
        setLoading(false);
      }
    };

    fetchScans();
  }, []);

  if (loading) {
    return (
      <div className="page-loading">
        <div className="loading-spinner-wrap">
          <svg className="loading-spinner" viewBox="0 0 24 24">
            <circle className="spinner-circle"></circle>
            <path className="spinner-path"></path>
          </svg>
          <p className="loading-text">Loading scan history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-error">
        <div className="alert-content">
          <strong className="alert-title">Error: </strong>
          <span className="alert-message">{error}</span>
        </div>
        <button onClick={() => navigate('/dashboard')} className="btn btn-sm btn-outline">
          Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="scan-history-page">
      <div className="scan-history-container">
        <div className="page-header-row">
          <h1 className="page-title">Scan History</h1>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn btn-outline btn-sm"
          >
            Back to Dashboard
          </button>
        </div>
        <div className="card table-card">
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Scan ID</th>
                  <th>Lab</th>
                  <th>Status</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {scans.length > 0 ? (
                  scans.map((scan) => (
                    <tr key={scan.id}>
                      <td className="font-mono">#{scan.id}</td>
                      <td>{scan.labName}</td>
                      <td>
                        <span className={`badge ${
                          scan.status === 'completed' || scan.status === 'generated' ? 'badge-success' :
                          scan.status === 'pending' ? 'badge-warning' :
                          'badge-danger'}`}
                        >
                          {scan.status}
                        </span>
                      </td>
                      <td>{new Date(scan.createdAt).toLocaleString()}</td>
                      <td>
                        <button
                          onClick={() => navigate(`/scan/${scan.id}`)}
                          className="btn btn-sm btn-outline"
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="table-empty">
                      No scans found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScanHistory;
