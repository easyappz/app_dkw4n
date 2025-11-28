import React, { useState, useEffect } from 'react';
import { getReferralStats, getReferralTree } from '../../api/referrals';
import './Analytics.css';

const Analytics = () => {
  const [stats, setStats] = useState(null);
  const [tree, setTree] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [statsResponse, treeResponse] = await Promise.all([
        getReferralStats(),
        getReferralTree({ max_depth: 10 })
      ]);
      
      setStats(statsResponse.data);
      setTree(treeResponse.data);
    } catch (err) {
      console.error('Error loading analytics:', err);
      setError('Ошибка загрузки аналитики');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      setError(null);
      
      const [statsResponse, treeResponse] = await Promise.all([
        getReferralStats(),
        getReferralTree({ max_depth: 10 })
      ]);
      
      setStats(statsResponse.data);
      setTree(treeResponse.data);
    } catch (err) {
      console.error('Error refreshing analytics:', err);
      setError('Ошибка обновления аналитики');
    } finally {
      setRefreshing(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', { 
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric' 
    });
  };

  const formatAmount = (amount) => {
    return new Intl.NumberFormat('ru-RU', { 
      minimumFractionDigits: 0,
      maximumFractionDigits: 2 
    }).format(amount);
  };

  const getUserTypeLabel = (userType) => {
    return userType === 'player' ? 'Игрок' : 'Инфлюенсер';
  };

  const ReferralTreeNode = ({ node }) => {
    return (
      <div className="tree-node">
        <div className="tree-node-content">
          <span className="node-level">Ур. {node.level}</span>
          <span className="node-username">{node.username}</span>
          <span className="node-type">{getUserTypeLabel(node.user_type)}</span>
          <span className="node-date">{formatDate(node.created_at)}</span>
        </div>
        {node.children && node.children.length > 0 && (
          <div className="tree-children">
            {node.children.map((child) => (
              <ReferralTreeNode key={child.id} node={child} />
            ))}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="analytics-page" data-easytag="id1-react/src/pages/Analytics/index.jsx">
        <div className="loading-container">
          <p>Загрузка аналитики...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-page" data-easytag="id1-react/src/pages/Analytics/index.jsx">
        <div className="error-container">
          <p className="error-message">{error}</p>
          <button onClick={loadAnalytics} className="retry-button">Повторить</button>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-page" data-easytag="id1-react/src/pages/Analytics/index.jsx">
      <div className="analytics-header">
        <h1>📊 Аналитика рефералов</h1>
        <button 
          className="refresh-button" 
          onClick={handleRefresh}
          disabled={refreshing}
        >
          {refreshing ? '🔄 Обновление...' : '🔄 Обновить'}
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="analytics-grid">
        <div className="stat-card">
          <div className="stat-label">Всего рефералов</div>
          <div className="stat-value">{stats?.total_referrals || 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Прямые рефералы</div>
          <div className="stat-value">{stats?.direct_referrals || 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Всего заработано</div>
          <div className="stat-value">{formatAmount(stats?.total_earned || 0)}</div>
        </div>
      </div>

      {/* Referral Tree */}
      <div className="referral-tree-section">
        <h2 className="section-title">🌳 Дерево рефералов</h2>
        {tree && tree.length > 0 ? (
          <div className="tree-container">
            {tree.map((node) => (
              <ReferralTreeNode key={node.id} node={node} />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">👥</div>
            <p>У вас пока нет рефералов</p>
          </div>
        )}
      </div>

      {/* Earnings Chart */}
      <div className="earnings-chart-section">
        <h2 className="section-title">💰 Статистика по уровням</h2>
        {stats?.level_breakdown && stats.level_breakdown.length > 0 ? (
          <table className="level-stats-table">
            <thead>
              <tr>
                <th>Уровень</th>
                <th>Количество</th>
                <th>Заработано</th>
              </tr>
            </thead>
            <tbody>
              {stats.level_breakdown.map((level) => (
                <tr key={level.level}>
                  <td>
                    <span className="level-indicator">Уровень {level.level}</span>
                  </td>
                  <td>{level.count}</td>
                  <td>{formatAmount(level.earned)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">
            <p>Нет данных по уровням</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Analytics;
