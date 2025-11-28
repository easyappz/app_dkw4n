import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProfile, getReferralLink } from '../../api/users';
import { getReferralStats } from '../../api/referrals';
import { getCurrentLevel } from '../../api/levels';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [referralLink, setReferralLink] = useState(null);
  const [stats, setStats] = useState(null);
  const [level, setLevel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copySuccess, setCopySuccess] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [profileData, linkData, statsData, levelData] = await Promise.all([
        getProfile(),
        getReferralLink(),
        getReferralStats(),
        getCurrentLevel()
      ]);
      setProfile(profileData);
      setReferralLink(linkData);
      setStats(statsData);
      setLevel(levelData);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyLink = async () => {
    if (referralLink && referralLink.referral_code) {
      try {
        const fullLink = `${window.location.origin}/register?ref=${referralLink.referral_code}`;
        await navigator.clipboard.writeText(fullLink);
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
      } catch (error) {
        console.error('Failed to copy:', error);
      }
    }
  };

  if (loading) {
    return (
      <div className="dashboard-container" data-easytag="id1-react/src/pages/Dashboard/index.jsx">
        <div className="dashboard-loading">Загрузка...</div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="dashboard-container" data-easytag="id1-react/src/pages/Dashboard/index.jsx">
        <div className="dashboard-error">Ошибка загрузки профиля</div>
      </div>
    );
  }

  const isInfluencer = profile.user_type === 'influencer';
  const currency = isInfluencer ? '₽' : 'V-Coins';
  const balance = isInfluencer ? profile.balance_rubles : profile.balance_vcoins;

  return (
    <div className="dashboard-container" data-easytag="id1-react/src/pages/Dashboard/index.jsx">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Личный кабинет</h1>
        <p className="dashboard-subtitle">Добро пожаловать, {profile.username}!</p>
      </div>

      <div className="dashboard-grid">
        {/* Balance Card */}
        <div className="dashboard-card balance-card">
          <div className="card-icon">💰</div>
          <div className="card-content">
            <h3 className="card-label">Баланс</h3>
            <div className="balance-value">
              {isInfluencer ? balance.toFixed(2) : balance}
              <span className="balance-currency">{currency}</span>
            </div>
            <div className="card-type">
              {isInfluencer ? 'Инфлюенсер' : 'Игрок'}
            </div>
          </div>
        </div>

        {/* Level Card */}
        <div className="dashboard-card level-card">
          <div className="card-icon">⭐</div>
          <div className="card-content">
            <h3 className="card-label">Текущий уровень</h3>
            <div className="level-name">{level?.level_name || 'Новичок'}</div>
            <div className="level-progress">
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${level?.progress_percentage || 0}%` }}
                ></div>
              </div>
              <div className="progress-text">
                {level?.current_points || 0} / {level?.points_for_next_level || 0} очков
              </div>
            </div>
          </div>
        </div>

        {/* Referral Link Card */}
        <div className="dashboard-card referral-card">
          <div className="card-icon">🔗</div>
          <div className="card-content">
            <h3 className="card-label">Реферальная ссылка</h3>
            <div className="referral-code">{referralLink?.referral_code || 'N/A'}</div>
            <div className="referral-link-container">
              <input 
                type="text" 
                className="referral-input"
                value={referralLink?.referral_code ? `${window.location.origin}/register?ref=${referralLink.referral_code}` : ''}
                readOnly
              />
              <button 
                className="copy-button"
                onClick={handleCopyLink}
              >
                {copySuccess ? '✓ Скопировано' : 'Копировать'}
              </button>
            </div>
          </div>
        </div>

        {/* Referral Stats Card */}
        <div className="dashboard-card stats-card">
          <div className="card-icon">👥</div>
          <div className="card-content">
            <h3 className="card-label">Статистика рефералов</h3>
            <div className="stats-grid">
              <div className="stat-item">
                <div className="stat-value">{stats?.total_referrals || 0}</div>
                <div className="stat-name">Всего рефералов</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{stats?.direct_referrals || 0}</div>
                <div className="stat-name">Прямых приглашений</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{stats?.total_earned || 0}</div>
                <div className="stat-name">Заработано {currency}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Section */}
      <div className="dashboard-navigation">
        <h2 className="navigation-title">Разделы</h2>
        <div className="navigation-grid">
          <button className="nav-card" onClick={() => navigate('/referrals')}>
            <div className="nav-icon">👥</div>
            <div className="nav-title">Рефералы</div>
            <div className="nav-description">Список приглашенных друзей</div>
          </button>
          <button className="nav-card" onClick={() => navigate('/analytics')}>
            <div className="nav-icon">📊</div>
            <div className="nav-title">Аналитика</div>
            <div className="nav-description">Статистика и отчеты</div>
          </button>
          <button className="nav-card" onClick={() => navigate('/bonuses')}>
            <div className="nav-icon">🎁</div>
            <div className="nav-title">Бонусы</div>
            <div className="nav-description">Доступные награды</div>
          </button>
          <button className="nav-card" onClick={() => navigate('/deposit')}>
            <div className="nav-icon">💳</div>
            <div className="nav-title">Пополнение</div>
            <div className="nav-description">Пополнить баланс</div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;