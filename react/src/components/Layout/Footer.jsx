import React from 'react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer" data-easytag="id3-react/src/components/Layout/Footer.jsx">
      <div className="footer-container">
        <div className="footer-section">
          <h3>V-Coins Gaming</h3>
          <p>Реферальная система для игроков и инфлюенсеров</p>
        </div>
        <div className="footer-section">
          <h4>Навигация</h4>
          <ul>
            <li><a href="/rules">Правила</a></li>
            <li><a href="/dashboard">Панель</a></li>
            <li><a href="/referrals">Рефералы</a></li>
          </ul>
        </div>
        <div className="footer-section">
          <h4>Контакты</h4>
          <p>support@vcoins-gaming.com</p>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2024 V-Coins Gaming. Все права защищены.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
