import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import Footer from './Footer';
import './Layout.css';

const Layout = ({ user, onLogout }) => {
  return (
    <div className="layout" data-easytag="id4-react/src/components/Layout/Layout.jsx">
      <Header user={user} onLogout={onLogout} />
      <div className="layout-body">
        {user && <Sidebar user={user} />}
        <main className="main-content">
          <Outlet />
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default Layout;
