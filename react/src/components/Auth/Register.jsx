import React, { useState } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { register } from '../../api/auth';
import './Auth.css';

const Register = ({ onRegister }) => {
  const [searchParams] = useSearchParams();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    user_type: 'player',
    referral_code: searchParams.get('ref') || '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }

    if (formData.password.length < 8) {
      setError('Пароль должен быть не менее 8 символов');
      return;
    }

    setLoading(true);

    try {
      const registerData = {
        username: formData.username,
        password: formData.password,
        user_type: formData.user_type,
      };

      if (formData.referral_code) {
        registerData.referral_code = formData.referral_code;
      }

      const response = await register(registerData);
      if (onRegister) {
        onRegister(response.data.user);
      }
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка регистрации. Попробуйте снова.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container" data-easytag="id6-react/src/components/Auth/Register.jsx">
      <div className="auth-card">
        <h1 className="auth-title">Регистрация</h1>
        <p className="auth-subtitle">Создайте аккаунт и начните зарабатывать</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="username">Имя пользователя</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              className="form-input"
              placeholder="Введите имя пользователя"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Пароль</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={8}
              className="form-input"
              placeholder="Минимум 8 символов"
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Подтвердите пароль</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              className="form-input"
              placeholder="Повторите пароль"
            />
          </div>

          <div className="form-group">
            <label htmlFor="user_type">Тип аккаунта</label>
            <select
              id="user_type"
              name="user_type"
              value={formData.user_type}
              onChange={handleChange}
              className="form-select"
            >
              <option value="player">Обычный игрок (V-Coins)</option>
              <option value="influencer">Инфлюенсер (Реальные деньги)</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="referral_code">Реферальный код (опционально)</label>
            <input
              type="text"
              id="referral_code"
              name="referral_code"
              value={formData.referral_code}
              onChange={handleChange}
              className="form-input"
              placeholder="Если есть реферальный код"
            />
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Регистрация...' : 'Зарегистрироваться'}
          </button>
        </form>

        <div className="auth-footer">
          <p>Уже есть аккаунт? <Link to="/login" className="auth-link">Войти</Link></p>
        </div>
      </div>
    </div>
  );
};

export default Register;
