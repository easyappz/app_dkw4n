import React, { useState, useEffect } from 'react';
import { getUsers, addBonus, confirmTournament, confirmDeposit, getStats, seedTestUsers } from '../../api/admin';
import './Admin.css';

const Admin = () => {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [seedLoading, setSeedLoading] = useState(false);
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [userTypeFilter, setUserTypeFilter] = useState('');
  
  // Forms
  const [bonusForm, setBonusForm] = useState({
    user_id: '',
    amount: '',
    reason: ''
  });
  
  const [tournamentForm, setTournamentForm] = useState({
    user_id: '',
    tournament_name: '',
    reward_amount: ''
  });
  
  const [depositForm, setDepositForm] = useState({
    transaction_id: ''
  });

  useEffect(() => {
    loadStats();
    loadUsers();
  }, [currentPage, searchTerm, userTypeFilter]);

  const loadStats = async () => {
    try {
      const response = await getStats();
      setStats(response.data);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  };

  const loadUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page: currentPage,
        page_size: 20
      };
      
      if (searchTerm) {
        params.search = searchTerm;
      }
      
      if (userTypeFilter) {
        params.user_type = userTypeFilter;
      }
      
      const response = await getUsers(params);
      setUsers(response.data.results);
      setTotalCount(response.data.count);
      setTotalPages(Math.ceil(response.data.count / 20));
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка загрузки пользователей');
    } finally {
      setLoading(false);
    }
  };

  const handleSeedTestUsers = async () => {
    setSeedLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await seedTestUsers();
      setSuccess(response.data.message || 'Тестовые пользователи успешно созданы!');
      loadStats();
      loadUsers();
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка создания тестовых пользователей');
    } finally {
      setSeedLoading(false);
    }
  };

  const handleBonusSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    
    try {
      await addBonus({
        user_id: parseInt(bonusForm.user_id),
        amount: parseFloat(bonusForm.amount),
        reason: bonusForm.reason
      });
      
      setSuccess('Бонус успешно начислен!');
      setBonusForm({ user_id: '', amount: '', reason: '' });
      loadStats();
      loadUsers();
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка начисления бонуса');
    }
  };

  const handleTournamentSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    
    try {
      await confirmTournament({
        user_id: parseInt(tournamentForm.user_id),
        tournament_name: tournamentForm.tournament_name,
        reward_amount: parseFloat(tournamentForm.reward_amount)
      });
      
      setSuccess('Турнир успешно подтвержден!');
      setTournamentForm({ user_id: '', tournament_name: '', reward_amount: '' });
      loadStats();
      loadUsers();
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка подтверждения турнира');
    }
  };

  const handleDepositSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    
    try {
      await confirmDeposit({
        transaction_id: parseInt(depositForm.transaction_id)
      });
      
      setSuccess('Депозит успешно подтвержден!');
      setDepositForm({ transaction_id: '' });
      loadStats();
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка подтверждения депозита');
    }
  };

  const handleSearch = (value) => {
    setSearchTerm(value);
    setCurrentPage(1);
  };

  const handleFilterChange = (value) => {
    setUserTypeFilter(value);
    setCurrentPage(1);
  };

  return (
    <div className="admin-page" data-easytag="id1-react/src/pages/Admin/index.jsx">
      <div className="admin-container">
        <div className="admin-header">
          <h1>🔐 Панель Администратора</h1>
          <p>Управление пользователями и системой</p>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        {/* Stats Dashboard */}
        {stats && (
          <div className="stats-dashboard">
            <div className="stat-card">
              <div className="stat-icon">👥</div>
              <div className="stat-label">Всего пользователей</div>
              <div className="stat-value">{stats.total_users}</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">🎮</div>
              <div className="stat-label">Игроки</div>
              <div className="stat-value">{stats.total_players}</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">⭐</div>
              <div className="stat-label">Инфлюенсеры</div>
              <div className="stat-value">{stats.total_influencers}</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">💰</div>
              <div className="stat-label">Начислено бонусов</div>
              <div className="stat-value">{stats.total_bonuses_paid.toLocaleString()}</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">💳</div>
              <div className="stat-label">Всего депозитов</div>
              <div className="stat-value">{stats.total_deposits.toLocaleString()}</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">⏳</div>
              <div className="stat-label">Ожидают подтверждения</div>
              <div className="stat-value">{stats.pending_deposits}</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📊</div>
              <div className="stat-label">Транзакций</div>
              <div className="stat-value">{stats.total_transactions}</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">🔥</div>
              <div className="stat-label">Активных за 30 дней</div>
              <div className="stat-value">{stats.active_users_last_30_days}</div>
            </div>
          </div>
        )}

        {/* Admin Actions */}
        <div className="admin-actions">
          {/* Seed Test Users */}
          <div className="action-card">
            <h3>🧪 Создать тестовых пользователей</h3>
            <p className="action-description">
              Создать 4 тестовых игрока-реферала для инфлюенсера Tim с симуляцией активности
            </p>
            <button 
              onClick={handleSeedTestUsers} 
              disabled={seedLoading}
              className="btn-submit btn-seed"
            >
              {seedLoading ? 'Создание...' : 'Создать тестовых пользователей'}
            </button>
          </div>

          {/* Manual Bonus Form */}
          <div className="action-card">
            <h3>💎 Начислить бонус</h3>
            <form onSubmit={handleBonusSubmit}>
              <div className="form-group">
                <label>ID пользователя</label>
                <input
                  type="number"
                  value={bonusForm.user_id}
                  onChange={(e) => setBonusForm({ ...bonusForm, user_id: e.target.value })}
                  required
                  placeholder="Введите ID пользователя"
                />
              </div>
              <div className="form-group">
                <label>Сумма</label>
                <input
                  type="number"
                  step="0.01"
                  value={bonusForm.amount}
                  onChange={(e) => setBonusForm({ ...bonusForm, amount: e.target.value })}
                  required
                  placeholder="Введите сумму"
                />
              </div>
              <div className="form-group">
                <label>Причина</label>
                <textarea
                  value={bonusForm.reason}
                  onChange={(e) => setBonusForm({ ...bonusForm, reason: e.target.value })}
                  required
                  placeholder="Укажите причину начисления"
                />
              </div>
              <button type="submit" className="btn-submit">
                Начислить бонус
              </button>
            </form>
          </div>

          {/* Tournament Confirmation Form */}
          <div className="action-card">
            <h3>🏆 Подтвердить турнир</h3>
            <form onSubmit={handleTournamentSubmit}>
              <div className="form-group">
                <label>ID пользователя</label>
                <input
                  type="number"
                  value={tournamentForm.user_id}
                  onChange={(e) => setTournamentForm({ ...tournamentForm, user_id: e.target.value })}
                  required
                  placeholder="Введите ID пользователя"
                />
              </div>
              <div className="form-group">
                <label>Название турнира</label>
                <input
                  type="text"
                  value={tournamentForm.tournament_name}
                  onChange={(e) => setTournamentForm({ ...tournamentForm, tournament_name: e.target.value })}
                  required
                  placeholder="Введите название турнира"
                />
              </div>
              <div className="form-group">
                <label>Сумма награды</label>
                <input
                  type="number"
                  step="0.01"
                  value={tournamentForm.reward_amount}
                  onChange={(e) => setTournamentForm({ ...tournamentForm, reward_amount: e.target.value })}
                  required
                  placeholder="Введите сумму награды"
                />
              </div>
              <button type="submit" className="btn-submit">
                Подтвердить турнир
              </button>
            </form>
          </div>

          {/* Deposit Confirmation Form */}
          <div className="action-card">
            <h3>💳 Подтвердить депозит</h3>
            <form onSubmit={handleDepositSubmit}>
              <div className="form-group">
                <label>ID транзакции</label>
                <input
                  type="number"
                  value={depositForm.transaction_id}
                  onChange={(e) => setDepositForm({ ...depositForm, transaction_id: e.target.value })}
                  required
                  placeholder="Введите ID транзакции"
                />
              </div>
              <button type="submit" className="btn-submit">
                Подтвердить депозит
              </button>
            </form>
          </div>
        </div>

        {/* Users Table */}
        <section className="users-section">
          <h2>👥 Управление пользователями</h2>
          
          <div className="table-controls">
            <input
              type="text"
              className="search-box"
              placeholder="🔍 Поиск по имени пользователя..."
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
            />
            <select
              className="filter-select"
              value={userTypeFilter}
              onChange={(e) => handleFilterChange(e.target.value)}
            >
              <option value="">Все типы</option>
              <option value="player">Игроки</option>
              <option value="influencer">Инфлюенсеры</option>
            </select>
          </div>

          {loading ? (
            <div className="loading">Загрузка пользователей...</div>
          ) : (
            <>
              <div className="users-table-container">
                <table className="users-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Имя пользователя</th>
                      <th>Тип</th>
                      <th>Баланс</th>
                      <th>Рефералов</th>
                      <th>Заработано</th>
                      <th>Дата регистрации</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user) => (
                      <tr key={user.id}>
                        <td>{user.id}</td>
                        <td>
                          {user.username}
                          {user.is_admin && <span className="admin-badge">ADMIN</span>}
                        </td>
                        <td>
                          <span className={`user-badge ${user.user_type}`}>
                            {user.user_type === 'player' ? 'Игрок' : 'Инфлюенсер'}
                          </span>
                        </td>
                        <td>{user.balance.toLocaleString()}</td>
                        <td>{user.total_referrals}</td>
                        <td>{user.total_earned.toLocaleString()}</td>
                        <td>{new Date(user.created_at).toLocaleDateString('ru-RU')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="pagination">
                <button
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  ← Назад
                </button>
                <span>Страница {currentPage} из {totalPages} (Всего: {totalCount})</span>
                <button
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  Вперед →
                </button>
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  );
};

export default Admin;