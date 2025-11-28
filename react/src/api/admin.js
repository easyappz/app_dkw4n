import instance from './axios';

/**
 * Get all users with pagination and filters (Admin only)
 * @param {Object} params - Query parameters
 * @param {number} params.page - Page number
 * @param {number} params.page_size - Items per page
 * @param {string} params.user_type - Filter by user type
 * @param {string} params.search - Search by username
 * @returns {Promise} Response with paginated users list
 */
export const getUsers = async (params = {}) => {
  const response = await instance.get('/api/admin/users', { params });
  return response;
};

/**
 * Manually assign bonus to a user (Admin only)
 * @param {Object} data - Bonus data
 * @param {number} data.user_id - User ID
 * @param {number} data.amount - Bonus amount
 * @param {string} data.reason - Reason for bonus
 * @returns {Promise} Response with bonus details
 */
export const addBonus = async (data) => {
  const response = await instance.post('/api/admin/bonuses', data);
  return response;
};

/**
 * Confirm tournament participation and reward user (Admin only)
 * @param {Object} data - Tournament data
 * @param {number} data.user_id - User ID
 * @param {string} data.tournament_name - Tournament name
 * @param {number} data.reward_amount - Reward amount
 * @returns {Promise} Response with transaction details
 */
export const confirmTournament = async (data) => {
  const response = await instance.post('/api/admin/confirm-tournament', data);
  return response;
};

/**
 * Confirm pending deposit (Admin only)
 * @param {Object} data - Deposit data
 * @param {number} data.transaction_id - Transaction ID
 * @returns {Promise} Response with transaction details
 */
export const confirmDeposit = async (data) => {
  const response = await instance.post('/api/admin/confirm-deposit', data);
  return response;
};

/**
 * Get system statistics (Admin only)
 * @returns {Promise} Response with system stats
 */
export const getStats = async () => {
  const response = await instance.get('/api/admin/stats');
  return response;
};

/**
 * Seed test users (Admin only)
 * @returns {Promise} Response with created users count
 */
export const seedTestUsers = async () => {
  const response = await instance.post('/api/admin/seed-test-users');
  return response;
};