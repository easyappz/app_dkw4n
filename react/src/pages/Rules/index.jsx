import React, { useState } from 'react';
import './Rules.css';

const Rules = () => {
  const [activeFaq, setActiveFaq] = useState(null);

  const levels = [
    {
      level: 1,
      name: 'Прямой реферал',
      bonus: '1000 V-Coins',
      description: 'Получайте вознаграждение за каждого приглашенного друга'
    },
    {
      level: 2,
      name: 'Второй уровень',
      bonus: '150 V-Coins',
      description: 'Бонус за рефералов ваших друзей'
    },
    {
      level: 3,
      name: 'Третий уровень',
      bonus: '100 V-Coins',
      description: 'Расширяйте свою сеть глубже'
    },
    {
      level: 4,
      name: 'Четвертый уровень',
      bonus: '75 V-Coins',
      description: 'Дополнительный доход от глубоких связей'
    },
    {
      level: 5,
      name: 'Пятый уровень',
      bonus: '50 V-Coins',
      description: 'Продолжайте зарабатывать на каждом уровне'
    },
    {
      level: 6,
      name: 'Шестой уровень',
      bonus: '25 V-Coins',
      description: 'Стабильный пассивный доход'
    }
  ];

  const bonusSteps = [
    {
      icon: '👤',
      title: 'Пригласите друга',
      description: 'Поделитесь своей реферальной ссылкой'
    },
    {
      icon: '✅',
      title: 'Друг регистрируется',
      description: 'Он создает аккаунт по вашей ссылке'
    },
    {
      icon: '💰',
      title: 'Получите бонус',
      description: '1000 V-Coins моментально на счет'
    },
    {
      icon: '🔄',
      title: 'Цепочка продолжается',
      description: 'Зарабатывайте на всех уровнях'
    }
  ];

  const faqs = [
    {
      question: 'Как работает реферальная программа?',
      answer: 'Приглашайте друзей по своей уникальной ссылке. За каждого зарегистрировавшегося друга вы получаете 1000 V-Coins. Когда ваш друг приглашает своего друга, вы получаете дополнительно 150 V-Coins. Система работает до 10 уровней глубины.'
    },
    {
      question: 'В чем разница между игроком и инфлюенсером?',
      answer: 'Обычные игроки получают виртуальные фишки (V-Coins), которые можно использовать в игре. Инфлюенсеры получают реальные деньги за приглашения и могут выводить их на свой счет.'
    },
    {
      question: 'Как стать инфлюенсером?',
      answer: 'Статус инфлюенсера можно получить при регистрации, выбрав соответствующий тип аккаунта. Этот статус предназначен для блогеров и активных промоутеров с аудиторией.'
    },
    {
      question: 'Есть ли лимит на количество рефералов?',
      answer: 'Нет, вы можете приглашать неограниченное количество друзей и получать бонусы за каждого из них на всех 10 уровнях реферальной системы.'
    },
    {
      question: 'Когда начисляются бонусы?',
      answer: 'Бонусы начисляются моментально после успешной регистрации реферала. Вы сразу увидите увеличение баланса в своем личном кабинете.'
    },
    {
      question: 'Можно ли обменять V-Coins на реальные деньги?',
      answer: 'V-Coins для обычных игроков предназначены для использования в игре. Для получения реальных денег необходимо иметь статус инфлюенсера.'
    }
  ];

  const rewardsTable = [
    { level: 1, player: '1000 V-Coins', influencer: '500 ₽' },
    { level: 2, player: '150 V-Coins', influencer: '75 ₽' },
    { level: 3, player: '100 V-Coins', influencer: '50 ₽' },
    { level: 4, player: '75 V-Coins', influencer: '37.50 ₽' },
    { level: 5, player: '50 V-Coins', influencer: '25 ₽' },
    { level: 6, player: '25 V-Coins', influencer: '12.50 ₽' },
    { level: 7, player: '20 V-Coins', influencer: '10 ₽' },
    { level: 8, player: '15 V-Coins', influencer: '7.50 ₽' },
    { level: 9, player: '10 V-Coins', influencer: '5 ₽' },
    { level: 10, player: '5 V-Coins', influencer: '2.50 ₽' }
  ];

  const toggleFaq = (index) => {
    setActiveFaq(activeFaq === index ? null : index);
  };

  return (
    <div className="rules-page" data-easytag="id1-react/src/pages/Rules/index.jsx">
      <div className="rules-container">
        <div className="rules-header">
          <h1>⚡ Правила Реферальной Программы</h1>
          <p>Зарабатывайте на приглашениях друзей и развивайте свою сеть до 10 уровней глубины</p>
        </div>

        <div className="rules-content">
          {/* Levels Section */}
          <section className="levels-section">
            <h2>🎯 Уровни Вознаграждений</h2>
            <div className="levels-grid">
              {levels.map((level) => (
                <div key={level.level} className="level-card">
                  <div className="level-number">Уровень {level.level}</div>
                  <h3>{level.name}</h3>
                  <div className="level-bonus">{level.bonus}</div>
                  <p className="level-description">{level.description}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Infographic Section */}
          <section className="infographic-section">
            <h2>📊 Как Это Работает</h2>
            <div className="bonus-flow">
              {bonusSteps.map((step, index) => (
                <React.Fragment key={index}>
                  <div className="bonus-step">
                    <div className="bonus-icon">{step.icon}</div>
                    <h4>{step.title}</h4>
                    <p>{step.description}</p>
                  </div>
                  {index < bonusSteps.length - 1 && <div className="arrow">→</div>}
                </React.Fragment>
              ))}
            </div>
          </section>

          {/* Rewards Table */}
          <section className="rewards-section">
            <h2>💎 Таблица Наград</h2>
            <div className="rewards-table-container">
              <table className="rewards-table">
                <thead>
                  <tr>
                    <th>Уровень</th>
                    <th>
                      <span className="user-type-badge player">Игрок</span>
                    </th>
                    <th>
                      <span className="user-type-badge influencer">Инфлюенсер</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {rewardsTable.map((row) => (
                    <tr key={row.level}>
                      <td>Уровень {row.level}</td>
                      <td>{row.player}</td>
                      <td>{row.influencer}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* FAQ Section */}
          <section className="faq-section">
            <h2>❓ Часто Задаваемые Вопросы</h2>
            <div className="faq-list">
              {faqs.map((faq, index) => (
                <div
                  key={index}
                  className={`faq-item ${activeFaq === index ? 'active' : ''}`}
                >
                  <div className="faq-question" onClick={() => toggleFaq(index)}>
                    <span>{faq.question}</span>
                    <span className="faq-toggle">▼</span>
                  </div>
                  <div className="faq-answer">
                    {faq.answer}
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default Rules;
