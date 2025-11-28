import React, { useState, useEffect } from 'react';
import { getBonuses } from '../../api/transactions';
import './Bonuses.css';

const Bonuses = () => {
  const [bonuses, setBonuses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [dateFilter, setDateFilter] = useState('all');

  useEffect(() => {
    loadBonuses();
  }, [page]);

  const loadBonuses = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await getBonuses({ page, page_size: 20 });
      
      setBonuses(response.data.results);
      setTotalCount(response.data.count);
      setTotalPages(Math.ceil(response.data.count / 20));
    } catch (err) {
      console.error('Error loading bonuses:', err);
      setError('Ошибка загрузки бонусов');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', { 
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatAmount = (amount) => {
    return new Intl.NumberFormat('ru-RU', { 
      minimumFractionDigits: 0,
      maximumFractionDigits: 2 
    }).format(amount);
  };

  const filterBonusesByDate = (bonusList) => {
    if (dateFilter === 'all') return bonusList;
    
    const now = new Date();
    const filtered = bonusList.filter((bonus) => {
      const bonusDate = new Date(bonus.created_at);
      const diffTime = Math.abs(now - bonusDate);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      switch (dateFilter) {
        case 'week':
          return diffDays <= 7;
        case 'month':
          return diffDays <= 30;
        case 'year':
          return diffDays <= 365;
        default:
          return true;
      }
    });
    
    return filtered;
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage);
    }
  };

  const filteredBonuses = filterBonusesByDate(bonuses);
  const totalAmount = filteredBonuses.reduce((sum, bonus) => sum + parseFloat(bonus.amount), 0);

  return (
    <div className="bonuses-page" data-easytag="id1-react/src/pages/Bonuses/index.jsx">
      <div className="bonuses-header">
        <h1>🎁 История бонусов</h1>
        <div className="bonuses-summary">
          <div className="summary-item">
            <span className="summary-label">Всего бонусов:</span>
            <span className="summary-value">{totalCount}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Сумма за период:</span>
            <span className="summary-value">{formatAmount(totalAmount)}</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="filter-group">
          <label>Период:</label>
          <select 
            value={dateFilter} 
            onChange={(e) => setDateFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">Все время</option>
            <option value="week">Неделя</option>
            <option value="month">Месяц</option>
            <option value="year">Год</option>
          </select>
        </div>
      </div>

      {/* Bonuses Table */}
      {loading ? (
        <div className="loading-container">
          <p>Загрузка бонусов...</p>
        </div>
      ) : error ? (
        <div className="error-container">
          <p className="error-message">{error}</p>
          <button onClick={loadBonuses} className="retry-button">Повторить</button>
        </div>
      ) : filteredBonuses.length > 0 ? (
        <>
          <div className="bonuses-table-container">
            <table className="bonuses-table">
              <thead>
                <tr>
                  <th>Дата</th>
                  <th>Источник</th>
                  <th>Уровень</th>
                  <th>Причина</th>
                  <th>Сумма</th>
                </tr>
              </thead>
              <tbody>
                {filteredBonuses.map((bonus) => (
                  <tr key={bonus.id}>
                    <td>{formatDate(bonus.created_at)}</td>
                    <td>
                      <span className="referral-username">{bonus.referral_username}</span>
                    </td>
                    <td>
                      <span className="level-badge">Уровень {bonus.referral_level}</span>
                    </td>
                    <td>{bonus.reason}</td>
                    <td>
                      <span className="amount-value">+{formatAmount(bonus.amount)}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button 
                onClick={() => handlePageChange(page - 1)} 
                disabled={page === 1}
                className="pagination-button"
              >
                ← Назад
              </button>
              <span className="pagination-info">
                Страница {page} из {totalPages}
              </span>
              <button 
                onClick={() => handlePageChange(page + 1)} 
                disabled={page === totalPages}
                className="pagination-button"
              >
                Вперед →
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="empty-state">
          <div className="empty-state-icon">🎁</div>
          <p>У вас пока нет бонусов</p>
          <p className="empty-state-hint">Приглашайте друзей, чтобы получать бонусы!</p>
        </div>
      )}
    </div>
  );
};

export default Bonuses;
