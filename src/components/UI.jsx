import { useState } from 'react';

/* ── Modal ──────────────────────────────────────────────── */
export function Modal({ title, onClose, children }) {
  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal-box">
        <div className="modal-title">{title}</div>
        {children}
      </div>
    </div>
  );
}

/* ── Search bar ─────────────────────────────────────────── */
export function SearchBar({ value, onChange, placeholder = 'Cari...' }) {
  return (
    <div className="search-bar">
      <span className="search-icon">🔍</span>
      <input
        type="text"
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
      />
    </div>
  );
}

/* ── Empty state ────────────────────────────────────────── */
export function EmptyState({ icon = '📭', message = 'Tidak ada data.' }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icon}</div>
      <p>{message}</p>
    </div>
  );
}

/* ── Stat card ──────────────────────────────────────────── */
export function StatCard({ label, value, sub, icon }) {
  return (
    <div className="stat-card">
      {icon && <div className="stat-icon">{icon}</div>}
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  );
}

/* ── Pill / Badge ───────────────────────────────────────── */
export function Pill({ children, variant = 'green' }) {
  return <span className={`pill pill-${variant}`}>{children}</span>;
}

/* ── Form group ─────────────────────────────────────────── */
export function FormGroup({ label, children }) {
  return (
    <div className="form-group">
      <label>{label}</label>
      {children}
    </div>
  );
}

/* ── Confirm delete hook ─────────────────────────────────── */
export function useConfirm() {
  const [state, setState] = useState({ open: false, message: '', resolve: null });

  function confirm(message) {
    return new Promise(resolve => {
      setState({ open: true, message, resolve });
    });
  }

  function handle(result) {
    state.resolve(result);
    setState({ open: false, message: '', resolve: null });
  }

  const ConfirmDialog = state.open ? (
    <div className="modal-overlay">
      <div className="modal-box" style={{ maxWidth: 360 }}>
        <div className="modal-title">Konfirmasi</div>
        <p style={{ fontSize: '.85rem', color: 'var(--gray4)', marginBottom: '1rem' }}>{state.message}</p>
        <div className="modal-actions">
          <button className="btn btn-ghost" onClick={() => handle(false)}>Batal</button>
          <button className="btn btn-danger" onClick={() => handle(true)}>Hapus</button>
        </div>
      </div>
    </div>
  ) : null;

  return { confirm, ConfirmDialog };
}
