import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Change password
export const changePassword = async (currentPassword: string, newPassword: string) => {
    const response = await axios.post(
        `${API_BASE_URL}/api/auth/change-password`,
        { current_password: currentPassword, new_password: newPassword },
        {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('auth')}`
            }
        }
    );
    return response.data;
};

// Get active sessions
export const getSessions = async () => {
    const response = await axios.get(
        `${API_BASE_URL}/api/auth/sessions`,
        {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('auth')}`
            }
        }
    );
    return response.data;
};

// Delete account
export const deleteAccount = async (password: string) => {
    const response = await axios.delete(
        `${API_BASE_URL}/api/auth/me`,
        {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('auth')}`
            },
            data: { password }
        }
    );
    return response.data;
};
