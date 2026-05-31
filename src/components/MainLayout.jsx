import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/apiClient';

import DashboardPage        from '../pages/DashboardPage';
import UsersPage            from '../pages/UsersPage';
import MenusPage            from '../pages/MenusPage';
import OrdersPage           from '../pages/OrdersPage';
import RecommendationsPage  from '../pages/RecommendationsPage';
import CatalogPage          from '../pages/CatalogPage';
import MyRecommendationsPage from '../pages/MyRecommendationsPage';
import OrderMenuPage        from '../pages/OrderMenuPage';

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
  const { currentUser, logout } = useAuth();
  const [page, setPage] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [menus, setMenus] = useState([]);
  const [orders, setOrders] = useState([]);
  const [users, setUsers] = useState([]);
  const [dataLoading, setDataLoading] = useState(true);
  const [dataError, setDataError] = useState('');

  const isAdmin = currentUser.role === 'admin';
  const nav = isAdmin ? ADMIN_NAV : USER_NAV;

  const loadData = useCallback(async () => {
    setDataLoading(true);
    setDataError('');
    try {
      const fetchedMenus = await api.getMenus();
      setMenus(fetchedMenus);

      if (isAdmin) {
        const fetchedUsers = await api.getUsers();
        setUsers(fetchedUsers);
        const usersById = Object.fromEntries(fetchedUsers.map(u => [u.id, u.name]));
        const fetchedOrders = await api.getAllOrders(usersById);
        setOrders(fetchedOrders);
      } else {
        const fetchedOrders = await api.getMyOrders();
        setOrders(fetchedOrders);
      }
    } catch (e) {
      setDataError('Gagal memuat data: ' + e.message);
    } finally {
      setDataLoading(false);
    }
  }, [isAdmin]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  function navigate(p) {
    setPage(p);
    setSidebarOpen(false);
  }

  useEffect(() => {
    const handler = e => navigate(e.detail);
    document.addEventListener('navigate', handler);
    return () => document.removeEventListener('navigate', handler);
  }, []);

  function renderPage() {
    if (dataLoading) {
      return (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 200, color: 'var(--gray4)', fontSize: '.9rem' }}>
          Memuat data...
        </div>
      );
    }
    if (dataError) {
      return (
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <div style={{ color: '#c0392b', fontSize: '.9rem', marginBottom: '1rem' }}>⚠️ {dataError}</div>
          <button className="btn btn-primary" onClick={loadData}>Coba Lagi</button>
        </div>
      );
    }

    switch (page) {
      case 'dashboard':
        return <DashboardPage menus={menus} orders={orders} users={users} />;
      case 'users':
        return <UsersPage users={users} setUsers={setUsers} setOrders={setOrders} />;
      case 'menus':
        return <MenusPage menus={menus} />;
      case 'orders':
        return <OrdersPage orders={orders} users={users} menus={menus} />;
      case 'recommendations':
        return <RecommendationsPage users={users} orders={orders} menus={menus} />;
      case 'catalog':
        return <CatalogPage menus={menus} />;
      case 'order-menu':
        return <OrderMenuPage menus={menus} orders={orders} setOrders={setOrders} />;
      case 'my-recommendations':
        return <MyRecommendationsPage orders={orders} />;
      default:
        return null;
    }
  }

  return (
    <div className="main-layout">
      <div
        className={`sidebar-overlay ${sidebarOpen ? 'show' : ''}`}
        onClick={() => setSidebarOpen(false)}
      />

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
