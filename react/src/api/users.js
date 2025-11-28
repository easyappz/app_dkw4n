import instance from './axios';

/**
 * Get user profile
 * @returns {Promise} User profile data
 */
export const getProfile = async () => {
  const response = await instance.get('/api/users/profile');
  return response.data;
};

/**
 * Update user profile
 * @param {Object} data - Profile update data
 * @returns {Promise} Updated profile data
 */
export const updateProfile = async (data) => {
  const response = await instance.patch('/api/users/profile', data);
  return response.data;
};

/**
 * Get referral link
 * @returns {Promise} Referral link and code
 */
export const getReferralLink = async () => {
  const response = await instance.get('/api/users/referral-link');
  return response.data;
};
