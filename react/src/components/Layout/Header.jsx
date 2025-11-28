import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Header.css';

const Header = ({ user, onLogout }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    if (onLogout) {
      onLogout();
    }
    navigate('/login');
  };

  return (
    <header className="header" data-easytag="id1-react/src/components/Layout/Header.jsx">
      <div className="header-container">
        <Link to="/" className="logo">
          <span className="logo-text">V-Coins</span>
          <span className="logo-glow">Gaming</span>
        </Link>

        <nav className="nav-menu">
          {user ? (
            <>
              <Link to="/dashboard" className="nav-link">Панель</Link>
              <Link to="/referrals" className="nav-link">Рефералы</Link>
              <Link to="/analytics" className="nav-link">Аналитика</Link>
              <Link to="/bonuses" className="nav-link">Бонусы</Link>
              {user.is_admin && (
                <Link to="/admin" className="nav-link admin-link">Админ</Link>
              )}
              <div className="user-info">
                <span className="username">{user.username}</span>
                <span className="balance">{user.balance.toFixed(2)} {user.user_type === 'player' ? 'V-Coins' : '₽'}</span>
              </div>
              <button onClick={handleLogout} className="btn-logout">Выход</button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">Вход</Link>
              <Link to="/register" className="nav-link btn-register">Регистрация</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;
