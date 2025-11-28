import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

const Home = () => {
  return (
    <div className="home-page" data-easytag="id7-react/src/pages/Home.jsx">
      <div className="hero-section">
        <h1 className="hero-title">
          <span className="neon-text">V-Coins</span> Gaming
        </h1>
        <p className="hero-subtitle">Реферальная система нового поколения</p>
        <p className="hero-description">
          Зарабатывайте виртуальные фишки или реальные деньги, приглашая друзей!
        </p>
        <div className="hero-buttons">
          <Link to="/register" className="btn-hero primary">Начать зарабатывать</Link>
          <Link to="/login" className="btn-hero secondary">Войти</Link>
        </div>
      </div>

      <div className="features-section">
        <h2 className="section-title">Преимущества системы</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">👥</div>
            <h3>10 уровней рефералов</h3>
            <p>Получайте бонусы от приглашенных друзей до 10 уровня глубины</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">💰</div>
            <h3>Два типа наград</h3>
            <p>V-Coins для игроков или реальные деньги для инфлюенсеров</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Детальная аналитика</h3>
            <p>Отслеживайте свою реферальную сеть и доходы в реальном времени</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🎁</div>
            <h3>Щедрые бонусы</h3>
            <p>1000 V-Coins за каждого приглашенного друга, 150 за друзей друзей</p>
          </div>
        </div>
      </div>

      <div className="how-it-works">
        <h2 className="section-title">Как это работает?</h2>
        <div className="steps-grid">
          <div className="step-card">
            <div className="step-number">1</div>
            <h3>Регистрация</h3>
            <p>Выберите тип аккаунта: игрок или инфлюенсер</p>
          </div>
          <div className="step-card">
            <div className="step-number">2</div>
            <h3>Получите ссылку</h3>
            <p>Получите уникальную реферальную ссылку</p>
          </div>
          <div className="step-card">
            <div className="step-number">3</div>
            <h3>Приглашайте друзей</h3>
            <p>Делитесь ссылкой с друзьями и знакомыми</p>
          </div>
          <div className="step-card">
            <div className="step-number">4</div>
            <h3>Зарабатывайте</h3>
            <p>Получайте бонусы за каждого приглашенного пользователя</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
