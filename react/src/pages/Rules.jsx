import React from 'react';
import './Rules.css';

const Rules = () => {
  return (
    <div className="rules-page" data-easytag="id13-react/src/pages/Rules.jsx">
      <h1 className="page-title">Правила и условия</h1>
      <div className="rules-content">
        <section className="rules-section">
          <h2>Как работает реферальная система?</h2>
          <p>Наша система позволяет зарабатывать на приглашении новых пользователей.</p>
        </section>

        <section className="rules-section">
          <h2>Типы пользователей</h2>
          <ul>
            <li><strong>Обычные игроки:</strong> получают виртуальные фишки (V-Coins)</li>
            <li><strong>Инфлюенсеры:</strong> получают реальные деньги</li>
          </ul>
        </section>

        <section className="rules-section">
          <h2>Бонусы для обычных игроков</h2>
          <ul>
            <li>Привел друга → получил 1000 V-Coins</li>
            <li>Его друг привел своего друга → получил еще 150 V-Coins</li>
            <li>И так далее по цепочке до 10 уровней</li>
          </ul>
        </section>
      </div>
    </div>
  );
};

export default Rules;
