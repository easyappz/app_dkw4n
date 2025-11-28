import { instance } from './axios';

export const register = (data) => {
  return instance.post('/api/auth/register', data);
};

export const login = (data) => {
  return instance.post('/api/auth/login', data);
};

export const logout = () => {
  return instance.post('/api/auth/logout');
};

export const getCurrentUser = () => {
  return instance.get('/api/auth/me');
};
