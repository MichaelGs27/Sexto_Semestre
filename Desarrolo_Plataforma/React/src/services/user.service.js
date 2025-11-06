import axios from 'axios';

const API_URL = 'http://localhost:3000/api';

export const getUserProfile = async () => {
  const user = JSON.parse(localStorage.getItem('user'));
  if (!user || !user.token) {
    throw new Error('No user token found');
  }

  try {
    const response = await axios.get(`${API_URL}/users/profile`, {
      headers: {
        'Authorization': `Bearer ${user.token}`
      }
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Error al obtener datos del usuario' };
  }
};