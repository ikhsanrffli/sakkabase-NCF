import { CATEGORY_ICONS } from '../data/initialData';

const BASE_URL = 'http://localhost:8000';
const TOKEN_KEY = 'sakka_token';

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(method, path, body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
  };
  if (body !== null) opts.body = JSON.stringify(body);
  const res = await fetch(`${BASE_URL}${path}`, opts);
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch {}
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  if (res.status === 204) return null;
  return res.json();
}

// ── Adapters ──────────────────────────────────────────────────────────────────

function adaptMenu(m) {
  const codeMatch = m.item_id.match(/^([A-Z0-9]+)/);
  return {
    id: m.item_id,
    code: codeMatch ? codeMatch[1] : m.item_id,
    dbId: m.id,
    name: m.nama,
    category: m.kategori,
    icon: CATEGORY_ICONS[m.kategori] || '🍽️',
  };
}

function adaptUser(u) {
  return { id: u.id, username: u.username, name: u.nama_lengkap, role: u.role, source: u.source };
}

function adaptOrder(o, usersById = {}) {
  return {
    id: o.id,
    userId: o.user_id,
    userName: usersById[o.user_id] || `User #${o.user_id}`,
    menuId: o.menu_item?.item_id || '',
    menuName: o.menu_item?.nama || '',
    date: o.tanggal,
    dbMenuId: o.menu_item_id,
  };
}

// ── API ───────────────────────────────────────────────────────────────────────

export const api = {
  // Auth
  login: async (username, password) => {
    const data = await request('POST', '/auth/login', { username, password });
    localStorage.setItem(TOKEN_KEY, data.access_token);
    return data;
  },
  logout: () => localStorage.removeItem(TOKEN_KEY),
  register: (nama_lengkap, username, password) =>
    request('POST', '/auth/register', { nama_lengkap, username, password }),
  getMe: async () => adaptUser(await request('GET', '/auth/me')),

  // Menus
  getMenus: async (kategori = null) => {
    const url = kategori ? `/menus?kategori=${encodeURIComponent(kategori)}` : '/menus';
    const data = await request('GET', url);
    return data.items.map(adaptMenu);
  },
  getCategories: () => request('GET', '/menus/categories'),

  // Orders
  createOrder: (menu_item_id) => request('POST', '/orders', { menu_item_id }),
  getMyOrders: async () => {
    const data = await request('GET', '/orders/my');
    return data.orders.map(o => adaptOrder(o));
  },
  getAllOrders: async (usersById = {}) => {
    const data = await request('GET', '/orders');
    return data.orders.map(o => adaptOrder(o, usersById));
  },

  // Recommendations
  getMyRecommendations: async () => {
    const data = await request('GET', '/recommendations/me');
    return data.items.map(item => ({ rank: item.rank, score: item.score, ...adaptMenu(item.menu_item) }));
  },
  getUserRecommendations: async (userId) => {
    const data = await request('GET', `/recommendations/${userId}`);
    return data.items.map(item => ({ rank: item.rank, score: item.score, ...adaptMenu(item.menu_item) }));
  },

  // Users (admin)
  getUsers: async () => {
    const data = await request('GET', '/users');
    return data.users.map(adaptUser);
  },
  deleteUser: (id) => request('DELETE', `/users/${id}`),

  // Model (admin)
  getModelStatus: () => request('GET', '/model/status'),
  getAllModelStatus: () => request('GET', '/model/status/all'),
  retrainModel: () => request('POST', '/model/retrain'),
};
