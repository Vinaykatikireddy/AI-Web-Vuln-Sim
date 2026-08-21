import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Update AI settings
export const updateAISettings = async (aiEndpoint: string, aiApiKey: string) => {
    const response = await axios.put(
        `${API_BASE_URL}/api/settings/ai`,
        { ai_endpoint: aiEndpoint, ai_api_key: aiApiKey },
        {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('auth')}`
            }
        }
    );
    return response.data;
};

// Clear all data
export const clearAllData = async () => {
    const response = await axios.post(
        `${API_BASE_URL}/api/settings/clear-data`,
        {},
        {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('auth')}`
            }
        }
    );
    return response.data;
};
