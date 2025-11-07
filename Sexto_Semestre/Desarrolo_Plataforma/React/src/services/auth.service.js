import axios from 'axios';

const API_URL = 'http://localhost:3000/api';

const register = async (name, email, password) => {
  try {
    const response = await axios.post(`${API_URL}/auth/register`, {
      name,
      email,
      password
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Error en el servidor' };
  }
};

const login = async (email, password) => {
  try {
    const response = await axios.post(`${API_URL}/auth/login`, {
      email,
      password
    });
    if (response.data && response.data.token) {
      const userData = {
        ...response.data.user, // Ensure we're getting the user object
        token: response.data.token
      };
      localStorage.setItem('user', JSON.stringify(userData));
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;
      return userData;
    }
    throw new Error('Invalid response format');
  } catch (error) {
    throw error.response?.data || { message: 'Error en el servidor' };
  }
};

const logout = () => {
  localStorage.removeItem('user');
  delete axios.defaults.headers.common['Authorization'];
};

export { register, login, logout };