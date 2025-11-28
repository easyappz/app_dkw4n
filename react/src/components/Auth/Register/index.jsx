import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { register } from '../../../api/auth';
import './Register.css';

const Register = ({ onRegister }) => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const refParam = searchParams.get('ref');

  const [formData, setFormData] = useState({
    username: '',
    password: '',
    user_type: 'player',
    referral_code: refParam || ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (refParam) {
      setFormData(prev => ({
        ...prev,
        referral_code: refParam
      }));
    }
  }, [refParam]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const payload = {
        username: formData.username,
        password: formData.password,
        user_type: formData.user_type
      };

      // Add referral_code only if it's not empty
      if (formData.referral_code && formData.referral_code.trim() !== '') {
        payload.referral_code = formData.referral_code.trim();
      }

      const response = await register(payload);

      if (response.data && response.data.user) {
        onRegister(response.data.user);
        navigate('/dashboard');
      }
    } catch (err) {
      console.error('Registration error:', err);
      if (err.response && err.response.data) {
        setError(err.response.data.error || err.response.data.detail || 'Ошибка регистрации');
      } else {
        setError('Не удалось зарегистрироваться. Попробуйте снова.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page" data-easytag="id3-react/src/components/Auth/Register/index.jsx">
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1 className="auth-title">Регистрация</h1>
            <p className="auth-subtitle">Создайте аккаунт и начните зарабатывать</p>
          </div>

          {error && (
            <div className="auth-error">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="username" className="form-label">
                Имя пользователя
              </label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="form-input"
                placeholder="Введите имя пользователя"
                required
                autoComplete="username"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">
                Пароль
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="form-input"
                placeholder="Введите пароль"
                required
                autoComplete="new-password"
              />
            </div>

            <div className="form-group">
              <label htmlFor="user_type" className="form-label">
                Тип аккаунта
              </label>
              <select
                id="user_type"
                name="user_type"
                value={formData.user_type}
                onChange={handleChange}
                className="form-select"
                required
              >
                <option value="player">Игрок (V-Coins)</option>
                <option value="influencer">Инфлюенсер (Реальные деньги)</option>
              </select>
              <div className="user-type-info">
                {formData.user_type === 'player' ? (
                  <p>🎮 Получай виртуальные фишки за рефералов</p>
                ) : (
                  <p>💎 Получай реальные деньги за рефералов</p>
                )}
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="referral_code" className="form-label">
                Реферальный код (опционально)
              </label>
              <input
                type="text"
                id="referral_code"
                name="referral_code"
                value={formData.referral_code}
                onChange={handleChange}
                className="form-input"
                placeholder="Введите код приглашения"
                autoComplete="off"
              />
              {refParam && (
                <div className="referral-badge">
                  ✓ Реферальный код применен из ссылки
                </div>
              )}
            </div>

            <button
              type="submit"
              className="auth-submit-button"
              disabled={loading}
            >
              {loading ? 'Регистрация...' : 'Зарегистрироваться'}
            </button>
          </form>

          <div className="auth-footer">
            <p className="auth-footer-text">
              Уже есть аккаунт?{' '}
              <Link to="/login" className="auth-link">
                Войти
              </Link>
            </p>
          </div>
        </div>

        <div className="auth-background">
          <div className="floating-shape shape-1"></div>
          <div className="floating-shape shape-2"></div>
          <div className="floating-shape shape-3"></div>
        </div>
      </div>
    </div>
  );
};

export default Register;
