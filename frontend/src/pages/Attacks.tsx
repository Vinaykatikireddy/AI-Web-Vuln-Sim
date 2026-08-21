import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { errorHandler } from '../utils/errorHandler';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const Attacks: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [attacks, setAttacks] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAttacks = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/labs/${id}/attacks`);
        setAttacks(response.data);
      } catch (err) {
        setError(errorHandler(err));
      } finally {
        setLoading(false);
      }
    };

    fetchAttacks();
  }, [id]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Attacks for Lab {id}</h1>
      <button
        onClick={() => navigate(`/lab/${id}`)}
        className="mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Back to Lab
      </button>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {attacks.map((attack) => (
          <div key={attack.id} className="p-4 border rounded shadow">
            <h2 className="text-xl font-semibold">{attack.name}</h2>
            <p className="text-gray-600">{attack.description}</p>
            <button
              onClick={() => navigate(`/lab/${id}/attack/${attack.id}`)}
              className="mt-2 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              Run Attack
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Attacks;