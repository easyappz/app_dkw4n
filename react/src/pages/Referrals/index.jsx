import React, { useState, useEffect } from 'react';
import { getReferrals } from '../../api/referrals';
import './Referrals.css';

const Referrals = () => {
  const [referrals, setReferrals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrevious, setHasPrevious] = useState(false);

  useEffect(() => {
    fetchReferrals();
  }, [page]);

  const fetchReferrals = async () => {
    try {
      setLoading(true);
      const data = await getReferrals(page, 10);
      setReferrals(data.results || []);
      setHasNext(!!data.next);
      setHasPrevious(!!data.previous);
      const total = data.count || 0;
      setTotalPages(Math.ceil(total / 10));
    } catch (error) {
      console.error('Error fetching referrals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNextPage = () => {
    if (hasNext) {
      setPage(prev => prev + 1);
    }
  };

  const handlePrevPage = () => {
    if (hasPrevious) {
      setPage(prev => prev - 1);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const getStatusText = (userType) => {
    return userType === 'influencer' ? 'Инфлюенсер' : 'Игрок';
  };

  const getStatusColor = (userType) => {
    return userType === 'influencer' ? 'status-influencer' : 'status-player';
  };

  if (loading && referrals.length === 0) {
    return (
      <div className="referrals-container" data-easytag="id1-react/src/pages/Referrals/index.jsx">
        <div className="referrals-loading">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="referrals-container" data-easytag="id1-react/src/pages/Referrals/index.jsx">
      <div className="referrals-header">
        <h1 className="referrals-title">Мои рефералы</h1>
        <p className="referrals-subtitle">Список приглашенных друзей</p>
      </div>

      {referrals.length === 0 ? (
        <div className="referrals-empty">
          <div className="empty-icon">👥</div>
          <p className="empty-text">У вас пока нет рефералов</p>
          <p className="empty-hint">Пригласите друзей и получайте бонусы!</p>
        </div>
      ) : (
        <>
          <div className="referrals-list">
            {referrals.map((referral, index) => (
              <div key={referral.id || index} className="referral-card">
                <div className="referral-avatar">
                  <div className="avatar-circle">
                    {referral.username ? referral.username.charAt(0).toUpperCase() : '?'}
                  </div>
                </div>
                <div className="referral-info">
                  <div className="referral-name">{referral.username || 'Неизвестно'}</div>
                  <div className="referral-details">
                    <span className={`referral-status ${getStatusColor(referral.user_type)}`}>
                      {getStatusText(referral.user_type)}
                    </span>
                    <span className="referral-level">Уровень {referral.level || 1}</span>
                  </div>
                </div>
                <div className="referral-stats">
                  <div className="stat-item">
                    <div className="stat-label">Дата регистрации</div>
                    <div className="stat-value">{formatDate(referral.created_at)}</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-label">Заработано бонусов</div>
                    <div className="stat-value bonus-value">
                      {referral.bonus_earned || 0}
                      <span className="bonus-currency">
                        {referral.user_type === 'influencer' ? ' ₽' : ' V-Coins'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="referrals-pagination">
              <button 
                className="pagination-button"
                onClick={handlePrevPage}
                disabled={!hasPrevious}
              >
                ← Предыдущая
              </button>
              <span className="pagination-info">
                Страница {page} из {totalPages}
              </span>
              <button 
                className="pagination-button"
                onClick={handleNextPage}
                disabled={!hasNext}
              >
                Следующая →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Referrals;
