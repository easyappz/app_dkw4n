import React, { useState, useEffect } from 'react';
import { createDeposit, getTransactions } from '../../api/transactions';
import { getCurrentUser } from '../../api/auth';
import './Deposit.css';

const Deposit = () => {
  const [user, setUser] = useState(null);
  const [amount, setAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('card');
  const [loading, setLoading] = useState(false);
  const [depositHistory, setDepositHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadUserData();
    loadDepositHistory();
  }, []);

  const loadUserData = async () => {
    try {
      const response = await getCurrentUser();
      setUser(response.data);
    } catch (err) {
      console.error('Error loading user data:', err);
    }
  };

  const loadDepositHistory = async () => {
    try {
      setHistoryLoading(true);
      const response = await getTransactions({ 
        page: 1, 
        page_size: 10,
        transaction_type: 'deposit' 
      });
      setDepositHistory(response.data.results);
    } catch (err) {
      console.error('Error loading deposit history:', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!amount || parseFloat(amount) <= 0) {
      setMessage({ type: 'error', text: 'Введите корректную сумму' });
      return;
    }

    try {
      setLoading(true);
      setMessage(null);
      
      await createDeposit({
        amount: parseFloat(amount),
        payment_method: paymentMethod
      });
      
      setMessage({ 
        type: 'success', 
        text: 'Заявка на пополнение успешно создана. Ожидайте подтверждения администратора.' 
      });
      setAmount('');
      
      // Reload history
      await loadDepositHistory();
    } catch (err) {
      console.error('Error creating deposit:', err);
      setMessage({ 
        type: 'error', 
        text: err.response?.data?.detail || 'Ошибка создания заявки на пополнение' 
      });
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

  const getStatusLabel = (status) => {
    const labels = {
      pending: 'Ожидает',
      confirmed: 'Подтверждено',
      cancelled: 'Отменено'
    };
    return labels[status] || status;
  };

  const getStatusClass = (status) => {
    return `status-badge status-${status}`;
  };

  const isInfluencer = user?.user_type === 'influencer';

  return (
    <div className="deposit-page" data-easytag="id1-react/src/pages/Deposit/index.jsx">
      <div className="deposit-header">
        <h1>💳 Пополнение счета</h1>
      </div>

      <div className="deposit-content">
        {/* Deposit Form */}
        <div className="deposit-form-section">
          <h2 className="section-title">Создать заявку на пополнение</h2>
          
          <form onSubmit={handleSubmit} className="deposit-form">
            <div className="form-group">
              <label htmlFor="amount">Сумма пополнения:</label>
              <input
                type="number"
                id="amount"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Введите сумму"
                min="0"
                step="0.01"
                required
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="paymentMethod">Способ оплаты:</label>
              <select
                id="paymentMethod"
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
                className="form-select"
              >
                <option value="card">Банковская карта</option>
                <option value="crypto">Криптовалюта</option>
                <option value="transfer">Банковский перевод</option>
              </select>
            </div>

            {message && (
              <div className={`message ${message.type}`}>
                {message.text}
              </div>
            )}

            <button type="submit" disabled={loading} className="submit-button">
              {loading ? 'Создание заявки...' : 'Создать заявку'}
            </button>
          </form>

          {/* Payment Instructions */}
          <div className="payment-instructions">
            <h3>📋 Инструкция по оплате:</h3>
            <ol>
              <li>Заполните форму выше и создайте заявку на пополнение</li>
              <li>После создания заявки свяжитесь с администратором для получения реквизитов</li>
              <li>Произведите оплату по предоставленным реквизитам</li>
              <li>Отправьте подтверждение оплаты администратору</li>
              <li>После проверки администратор подтвердит пополнение</li>
            </ol>
          </div>
        </div>

        {/* Withdrawal Section for Influencers */}
        {isInfluencer && (
          <div className="withdrawal-section">
            <h2 className="section-title">💸 Вывод средств</h2>
            <div className="withdrawal-info">
              <p>Для вывода средств свяжитесь с администратором.</p>
              <p className="balance-info">
                Доступно для вывода: <span className="balance-amount">{formatAmount(user.balance)}</span>
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Deposit History */}
      <div className="deposit-history-section">
        <h2 className="section-title">📜 История пополнений</h2>
        
        {historyLoading ? (
          <div className="loading-container">
            <p>Загрузка истории...</p>
          </div>
        ) : depositHistory.length > 0 ? (
          <div className="history-table-container">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Дата</th>
                  <th>Сумма</th>
                  <th>Статус</th>
                  <th>Описание</th>
                </tr>
              </thead>
              <tbody>
                {depositHistory.map((transaction) => (
                  <tr key={transaction.id}>
                    <td>{formatDate(transaction.created_at)}</td>
                    <td className="amount-cell">{formatAmount(transaction.amount)}</td>
                    <td>
                      <span className={getStatusClass(transaction.status)}>
                        {getStatusLabel(transaction.status)}
                      </span>
                    </td>
                    <td>{transaction.description || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">💳</div>
            <p>История пополнений пуста</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Deposit;
