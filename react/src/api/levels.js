import instance from './axios';

/**
 * Get current level and progress
 * @returns {Promise} Current level and progress data
 */
export const getCurrentLevel = async () => {
  const response = await instance.get('/api/levels/current');
  return response.data;
};

/**
 * Get all levels
 * @returns {Promise} List of all levels
 */
export const getLevels = async () => {
  const response = await instance.get('/api/levels');
  return response.data;
};
