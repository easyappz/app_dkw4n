import axiosInstance from './axios';

export const getTransactions = async (params = {}) => {
  const { page = 1, page_size = 10, transaction_type } = params;
  const queryParams = new URLSearchParams();
  
  queryParams.append('page', page);
  queryParams.append('page_size', page_size);
  
  if (transaction_type) {
    queryParams.append('transaction_type', transaction_type);
  }
  
  return axiosInstance.get(`/api/transactions?${queryParams.toString()}`);
};

export const createDeposit = async (data) => {
  return axiosInstance.post('/api/transactions/deposit', data);
};

export const getBonuses = async (params = {}) => {
  const { page = 1, page_size = 10 } = params;
  const queryParams = new URLSearchParams();
  
  queryParams.append('page', page);
  queryParams.append('page_size', page_size);
  
  return axiosInstance.get(`/api/bonuses?${queryParams.toString()}`);
};
