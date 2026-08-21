import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { errorHandler } from '../utils/errorHandler';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const ScanHistory: React.FC = () => {
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchScans = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/scans/history`);
        setScans(response.data);
      } catch (err) {
        setError(errorHandler(err));
      } finally {
        setLoading(false);
      }
    };

    fetchScans();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Scan History</h1>
      <button
        onClick={() => navigate('/dashboard')}
        className="mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Back to Dashboard
      </button>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border">
          <thead>
            <tr>
              <th className="py-2 px-4 border">Scan ID</th>
              <th className="py-2 px-4 border">Lab</th>
              <th className="py-2 px-4 border">Status</th>
              <th className="py-2 px-4 border">Date</th>
              <th className="py-2 px-4 border">Actions</th>
            </tr>
          </thead>
          <tbody>
            {scans.map((scan) => (
              <tr key={scan.id}>
                <td className="py-2 px-4 border">{scan.id}</td>
                <td className="py-2 px-4 border">{scan.labName}</td>
                <td className="py-2 px-4 border">{scan.status}</td>
                <td className="py-2 px-4 border">{new Date(scan.createdAt).toLocaleString()}</td>
                <td className="py-2 px-4 border">
                  <button
                    onClick={() => navigate(`/scan/${scan.id}`)}
                    className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ScanHistory;