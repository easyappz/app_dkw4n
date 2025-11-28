import instance from './axios';

/**
 * Get referrals list
 * @param {number} page - Page number
 * @param {number} pageSize - Number of items per page
 * @returns {Promise} Paginated list of referrals
 */
export const getReferrals = async (page = 1, pageSize = 10) => {
  const response = await instance.get('/api/referrals', {
    params: {
      page,
      page_size: pageSize
    }
  });
  return response.data;
};

/**
 * Get referral statistics
 * @returns {Promise} Referral statistics
 */
export const getReferralStats = async () => {
  const response = await instance.get('/api/referrals/stats');
  return response.data;
};

/**
 * Get referral tree
 * @param {number} maxDepth - Maximum depth of referral tree
 * @returns {Promise} Referral tree structure
 */
export const getReferralTree = async (maxDepth = 10) => {
  const response = await instance.get('/api/referrals/tree', {
    params: {
      max_depth: maxDepth
    }
  });
  return response.data;
};
