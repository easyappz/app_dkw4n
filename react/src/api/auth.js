import axiosInstance from './axios';

/**
 * Register a new user
 * @param {Object} data - Registration data
 * @param {string} data.username - Username
 * @param {string} data.password - Password
 * @param {string} data.user_type - User type (player or influencer)
 * @param {string} [data.referral_code] - Optional referral code
 * @returns {Promise} Response with user data
 */
export const register = async (data) => {
  const response = await axiosInstance.post('/api/auth/register', data);
  return response;
};

/**
 * Login user
 * @param {Object} data - Login credentials
 * @param {string} data.username - Username
 * @param {string} data.password - Password
 * @returns {Promise} Response with user data
 */
export const login = async (data) => {
  const response = await axiosInstance.post('/api/auth/login', data);
  return response;
};

/**
 * Logout current user
 * @returns {Promise} Response with logout confirmation
 */
export const logout = async () => {
  const response = await axiosInstance.post('/api/auth/logout');
  return response;
};

/**
 * Get current authenticated user
 * @returns {Promise} Response with current user data
 */
export const getCurrentUser = async () => {
  const response = await axiosInstance.get('/api/auth/me');
  return response;
};
