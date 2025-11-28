import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = ({ user }) => {
  if (!user) return null;

  const menuItems = [
    { path: '/dashboard', label: 'Панель управления', icon: '📊' },
    { path: '/referrals', label: 'Мои рефералы', icon: '👥' },
    { path: '/analytics', label: 'Аналитика', icon: '📈' },
    { path: '/bonuses', label: 'Бонусы', icon: '🎁' },
    { path: '/deposit', label: 'Пополнение', icon: '💰' },
    { path: '/rules', label: 'Правила', icon: '📋' },
  ];

  if (user.is_admin) {
    menuItems.push({ path: '/admin', label: 'Админ панель', icon: '⚙️' });
  }

  return (
    <aside className="sidebar" data-easytag="id2-react/src/components/Layout/Sidebar.jsx">
      <div className="sidebar-content">
        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <span className="sidebar-icon">{item.icon}</span>
              <span className="sidebar-label">{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
    </aside>
  );
};

export default Sidebar;
