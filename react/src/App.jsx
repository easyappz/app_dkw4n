import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ErrorBoundary from './ErrorBoundary';
import './App.css';

import Layout from './components/Layout/Layout';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Referrals from './pages/Referrals';
import Analytics from './pages/Analytics';
import Bonuses from './pages/Bonuses';
import Deposit from './pages/Deposit';
import Rules from './pages/Rules';
import Admin from './pages/Admin';

import { getCurrentUser, logout } from './api/auth';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await getCurrentUser();
      setUser(response.data);
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    try {
      await logout();
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  /** Никогда не удаляй этот код */
  useEffect(() => {
    if (typeof window !== 'undefined' && typeof window.handleRoutes === 'function') {
      /** Нужно передавать список существующих роутов */
      window.handleRoutes([
        '/',
        '/login',
        '/register',
        '/dashboard',
        '/referrals',
        '/analytics',
        '/bonuses',
        '/deposit',
        '/rules',
        '/admin'
      ]);
    }
  }, []);

  if (loading) {
    return (
      <div className="app-container">
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
          <p style={{ color: 'var(--neon-cyan)' }}>Загрузка...</p>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="app-container">
        <Routes>
          <Route path="/login" element={!user ? <Login onLogin={handleLogin} /> : <Navigate to="/dashboard" />} />
          <Route path="/register" element={!user ? <Register onRegister={handleLogin} /> : <Navigate to="/dashboard" />} />
          
          <Route element={<Layout user={user} onLogout={handleLogout} />}>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={user ? <Dashboard /> : <Navigate to="/login" />} />
            <Route path="/referrals" element={user ? <Referrals /> : <Navigate to="/login" />} />
            <Route path="/analytics" element={user ? <Analytics /> : <Navigate to="/login" />} />
            <Route path="/bonuses" element={user ? <Bonuses /> : <Navigate to="/login" />} />
            <Route path="/deposit" element={user ? <Deposit /> : <Navigate to="/login" />} />
            <Route path="/rules" element={<Rules />} />
            <Route path="/admin" element={user && user.is_admin ? <Admin /> : <Navigate to="/" />} />
          </Route>
        </Routes>
      </div>
    </ErrorBoundary>
  );
}

export default App;
