import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import './Home.css';

const Home = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const refParam = searchParams.get('ref');
    if (refParam) {
      navigate(`/register?ref=${refParam}`, { replace: true });
    }
  }, [searchParams, navigate]);

  const handleRegister = () => {
    navigate('/register');
  };

  return (
    <div className="home-page" data-easytag="id1-react/src/pages/Home/index.jsx">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            <span className="neon-text">Реферальная</span>
            <br />
            <span className="neon-text-secondary">Игровая Программа</span>
          </h1>
          <p className="hero-description">
            Приводи друзей, получай бонусы и зарабатывай на каждом уровне!
            <br />
            Виртуальные фишки для игроков, реальные деньги для инфлюенсеров.
          </p>
          <div className="hero-buttons">
            <button className="cta-button primary-cta" onClick={handleRegister}>
              Начать зарабатывать
            </button>
            <button className="cta-button secondary-cta" onClick={() => navigate('/login')}>
              Войти
            </button>
          </div>
        </div>
        <div className="hero-visual">
          <div className="floating-card card-1"></div>
          <div className="floating-card card-2"></div>
          <div className="floating-card card-3"></div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="benefits-section">
        <h2 className="section-title">Преимущества для всех</h2>
        <div className="benefits-grid">
          <div className="benefit-card player-card">
            <div className="benefit-icon">🎮</div>
            <h3 className="benefit-title">Для игроков</h3>
            <ul className="benefit-list">
              <li>Получай <span className="highlight">1000 V-Coins</span> за каждого друга</li>
              <li>Бонусы со второго уровня: <span className="highlight">150 V-Coins</span></li>
              <li>Неограниченный потенциал заработка фишек</li>
              <li>Обменивай фишки на игровые привилегии</li>
            </ul>
          </div>
          <div className="benefit-card influencer-card">
            <div className="benefit-icon">💎</div>
            <h3 className="benefit-title">Для инфлюенсеров</h3>
            <ul className="benefit-list">
              <li>Получай <span className="highlight">реальные деньги</span> за рефералов</li>
              <li>Эксклюзивные бонусы и повышенные ставки</li>
              <li>Аналитика и статистика в реальном времени</li>
              <li>Приоритетная поддержка 24/7</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Levels Section */}
      <section className="levels-section">
        <h2 className="section-title">Уровни наград</h2>
        <p className="section-subtitle">
          Поднимайся по уровням и получай больше бонусов
        </p>
        <div className="levels-grid">
          <div className="level-card silver-level">
            <div className="level-badge">🥈</div>
            <h3 className="level-name">Серебро</h3>
            <div className="level-requirement">0-10 рефералов</div>
            <div className="level-rewards">
              <div className="reward-item">
                <span className="reward-label">Игроки:</span>
                <span className="reward-value">1000 V-Coins</span>
              </div>
              <div className="reward-item">
                <span className="reward-label">Инфлюенсеры:</span>
                <span className="reward-value">Базовая ставка</span>
              </div>
            </div>
          </div>
          <div className="level-card gold-level">
            <div className="level-badge">🥇</div>
            <h3 className="level-name">Золото</h3>
            <div className="level-requirement">11-50 рефералов</div>
            <div className="level-rewards">
              <div className="reward-item">
                <span className="reward-label">Игроки:</span>
                <span className="reward-value">1500 V-Coins</span>
              </div>
              <div className="reward-item">
                <span className="reward-label">Инфлюенсеры:</span>
                <span className="reward-value">+20% к ставке</span>
              </div>
            </div>
          </div>
          <div className="level-card platinum-level">
            <div className="level-badge">💎</div>
            <h3 className="level-name">Платина</h3>
            <div className="level-requirement">50+ рефералов</div>
            <div className="level-rewards">
              <div className="reward-item">
                <span className="reward-label">Игроки:</span>
                <span className="reward-value">2000 V-Coins</span>
              </div>
              <div className="reward-item">
                <span className="reward-label">Инфлюенсеры:</span>
                <span className="reward-value">+50% к ставке</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="how-it-works-section">
        <h2 className="section-title">Как это работает</h2>
        <div className="steps-container">
          <div className="step-card">
            <div className="step-number">1</div>
            <h3 className="step-title">Регистрация</h3>
            <p className="step-description">
              Создай аккаунт и выбери тип: игрок или инфлюенсер
            </p>
          </div>
          <div className="step-arrow">→</div>
          <div className="step-card">
            <div className="step-number">2</div>
            <h3 className="step-title">Получи ссылку</h3>
            <p className="step-description">
              Твоя уникальная реферальная ссылка появится в личном кабинете
            </p>
          </div>
          <div className="step-arrow">→</div>
          <div className="step-card">
            <div className="step-number">3</div>
            <h3 className="step-title">Приглашай друзей</h3>
            <p className="step-description">
              Делись ссылкой и получай бонусы за каждого приглашенного
            </p>
          </div>
          <div className="step-arrow">→</div>
          <div className="step-card">
            <div className="step-number">4</div>
            <h3 className="step-title">Зарабатывай</h3>
            <p className="step-description">
              Получай награды со всех уровней реферальной сети
            </p>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="final-cta-section">
        <div className="final-cta-content">
          <h2 className="final-cta-title">
            Готов начать зарабатывать?
          </h2>
          <p className="final-cta-description">
            Присоединяйся к тысячам игроков и инфлюенсеров уже сегодня!
          </p>
          <button className="cta-button large-cta" onClick={handleRegister}>
            Зарегистрироваться бесплатно
          </button>
        </div>
      </section>
    </div>
  );
};

export default Home;
