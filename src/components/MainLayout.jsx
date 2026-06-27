import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { MENUS_DATA, ORDERS_DATA } from '../data/initialData';
import { API_BASE } from '../utils/api';

import DashboardPage        from '../pages/DashboardPage';
import UsersPage            from '../pages/UsersPage';
import MenusPage            from '../pages/MenusPage';
import OrdersPage           from '../pages/OrdersPage';
import RecommendationsPage  from '../pages/RecommendationsPage';
import CatalogPage           from '../pages/CatalogPage';
import MyRecommendationsPage from '../pages/MyRecommendationsPage';
import OrderMenuPage         from '../pages/OrderMenuPage';

const ADMIN_NAV = [
  { group: 'Utama', items: [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  ]},
  { group: 'Manajemen Data', items: [
    { id: 'users',  label: 'Data Pengguna', icon: '👥' },
    { id: 'menus',  label: 'Data Menu',     icon: '🍽️' },
    { id: 'orders', label: 'Data Pemesanan',icon: '📋' },
  ]},
  { group: 'Sistem', items: [
    { id: 'recommendations', label: 'Rekomendasi Menu', icon: '⭐' },
  ]},
];

const USER_NAV = [
  { group: 'Menu', items: [
    { id: 'dashboard',          label: 'Dashboard',     icon: '📊' },
    { id: 'order-menu',         label: 'Pesan Menu',    icon: '🛒' },
    { id: 'catalog',            label: 'Lihat Menu',    icon: '🍽️' },
    { id: 'my-recommendations', label: 'Rekomendasiku', icon: '⭐' },
  ]},
];

const PAGE_TITLES = {
  dashboard: 'Dashboard',
  users: 'Manajemen Data Pengguna',
  menus: 'Manajemen Data Menu',
  orders: 'Data Pemesanan',
  recommendations: 'Rekomendasi Menu',
  'order-menu': 'Pesan Menu',
  catalog: 'Katalog Menu',
  'my-recommendations': 'Rekomendasi Untukku',
};

export default function MainLayout() {
  const { currentUser, users, setUsers, logout } = useAuth();
  const [page, setPage] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [menus, setMenus] = useState(MENUS_DATA);
  const [orders, setOrders] = useState(ORDERS_DATA);

  const nav = currentUser.role === 'admin' ? ADMIN_NAV : USER_NAV;

  // Tahap 2: muat menu & pesanan dari MySQL (fallback ke data bawaan bila backend mati).
  useEffect(() => {
    fetch(`${API_BASE}/db/menus`)
      .then(r => r.json())
      .then(d => { if (Array.isArray(d) && d.length) setMenus(d); })
      .catch(() => {});
    fetch(`${API_BASE}/db/orders`)
      .then(r => r.json())
      .then(d => { if (Array.isArray(d)) setOrders(d); })
      .catch(() => {});
  }, []);

  function navigate(p) {
    setPage(p);
    setSidebarOpen(false);
  }

  // Listen for navigate events dispatched from child pages (e.g. dashboard quick-action buttons)
  useEffect(() => {
    const handler = e => navigate(e.detail);
    document.addEventListener('navigate', handler);
    return () => document.removeEventListener('navigate', handler);
  }, []);

  const sharedProps = { menus, setMenus, orders, setOrders, users, setUsers };

  function renderPage() {
    switch (page) {
      case 'dashboard':          return <DashboardPage {...sharedProps} />;
      case 'users':              return <UsersPage {...sharedProps} />;
      case 'menus':              return <MenusPage {...sharedProps} />;
      case 'orders':             return <OrdersPage {...sharedProps} />;
      case 'recommendations':    return <RecommendationsPage {...sharedProps} />;
      case 'catalog':            return <CatalogPage menus={menus} orders={orders} />;
      case 'order-menu':         return <OrderMenuPage menus={menus} orders={orders} setOrders={setOrders} />;
      case 'my-recommendations': return <MyRecommendationsPage menus={menus} orders={orders} />;
      default:                   return null;
    }
  }

  return (
    <div className="main-layout">
      {/* Sidebar overlay (mobile) */}
      <div
        className={`sidebar-overlay ${sidebarOpen ? 'show' : ''}`}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <div className="sb-icon">S</div>
          <div className="sb-brand-text">
            Sakka Base
            <span>Menu Rec. System</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          {nav.map(group => (
            <div key={group.group}>
              <div className="nav-label">{group.group}</div>
              {group.items.map(item => (
                <div
                  key={item.id}
                  className={`nav-item ${page === item.id ? 'active' : ''}`}
                  onClick={() => navigate(item.id)}
                >
                  <span className="nav-item-icon">{item.icon}</span>
                  {item.label}
                </div>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="user-chip">
            <div className="user-avatar">
              {currentUser.name.charAt(0).toUpperCase()}
            </div>
            <div className="user-info">
              <div className="user-name">{currentUser.name}</div>
              <div className="user-role">{currentUser.role}</div>
            </div>
            <button className="logout-btn" onClick={logout} title="Logout">✕</button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="main-content">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="hamburger-btn"
              onClick={() => setSidebarOpen(v => !v)}
              aria-label="Toggle sidebar"
            >
              ☰
            </button>
            <div className="topbar-title">{PAGE_TITLES[page] || page}</div>
          </div>
          <div>
            <span className="badge-role">{currentUser.role}</span>
          </div>
        </header>

        <main className="content-area animate-in" key={page}>
          {renderPage()}
        </main>
      </div>
    </div>
  );
}
