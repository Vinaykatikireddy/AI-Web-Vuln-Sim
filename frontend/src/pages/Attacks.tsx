import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { errorHandler } from '../utils/errorHandler';

const API_BASE_URL = import.meta.env.VITE_AWVS_BASE_URL;

const Attacks: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [attacks, setAttacks] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAttacks = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/labs/${id}/attacks`);
        setAttacks(response.data);
      } catch (err) {
        setError(errorHandler(err));
      } finally {
        setLoading(false);
      }
    };

    fetchAttacks();
  }, [id]);

  if (loading) {
    return (
      <div className="page-loading">
        <div className="loading-spinner-wrap">
          <svg className="loading-spinner" viewBox="0 0 24 24">
            <circle className="spinner-circle"></circle>
            <path className="spinner-path"></path>
          </svg>
          <p className="loading-text">Loading attacks...</p>
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
        <button onClick={() => navigate(`/lab/${id}`)} className="btn btn-sm btn-outline">
          Back to Lab
        </button>
      </div>
    );
  }

  return (
    <div className="attacks-page">
      <div className="attacks-container">
        <div className="page-header-row">
          <h1 className="page-title">Attacks for Lab {id}</h1>
          <button
            onClick={() => navigate(`/lab/${id}`)}
            className="btn btn-outline btn-sm"
          >
            Back to Lab
          </button>
        </div>
        <div className="attacks-grid">
          {attacks.map((attack) => (
            <div key={attack.id} className="card attack-card">
              <div className="card-body">
                <h2 className="attack-title">{attack.name}</h2>
                <p className="attack-desc">{attack.description}</p>
                <button
                  onClick={() => navigate(`/lab/${id}/attack/${attack.id}`)}
                  className="btn btn-primary btn-sm"
                >
                  Run Attack
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Attacks;
