"""
db.py — Lapisan basis data MySQL (SQLAlchemy) untuk Sakka Base.

Memetakan tabel yang sudah dibuat oleh database/sakkabase_seed.sql:
users, menu_items, orders, order_details, recommendations, model_log.

Koneksi diatur lewat environment variable DATABASE_URL. Contoh untuk MySQL:
  set DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/sakkabase_ncf   (Windows)
  export DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/sakkabase_ncf
Jika tidak diset, default ke MySQL lokal tanpa password, database 'sakkabase_ncf'.
"""
import os
from datetime import datetime, date
from sqlalchemy import (create_engine, Column, Integer, String, Date, DateTime,
                        ForeignKey)
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "mysql+pymysql://root:@127.0.0.1:3306/sakkabase_ncf",
)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nama_lengkap = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(10), default="user")            # 'admin' | 'user'
    source = Column(String(12), default="historical")    # 'historical' | 'registered'
    created_at = Column(DateTime, default=datetime.utcnow)


class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String(100), nullable=False)        # kode menu, mis. 'A00A'
    nama_menu = Column(String(150), nullable=False)
    kategori = Column(String(100))
    price = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total = Column(Integer, default=0)
    tanggal = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)


class OrderDetail(Base):
    __tablename__ = "order_details"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    qty = Column(Integer, default=1)
    price = Column(Integer, default=0)


# --- Engine & Session (lazy: dibuat saat pertama dipakai) ---
_engine = None
_Session = None


def get_session():
    """Kembalikan SQLAlchemy Session. Membuat engine pada pemanggilan pertama."""
    global _engine, _Session
    if _engine is None:
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
        _Session = sessionmaker(bind=_engine, autoflush=False, future=True)
    return _Session()


def init_sqlite_for_test(path="sqlite:///./_test_sakka.db"):
    """Khusus pengujian lokal tanpa MySQL: buat semua tabel di SQLite."""
    global _engine, _Session
    _engine = create_engine(path, future=True)
    Base.metadata.create_all(_engine)
    _Session = sessionmaker(bind=_engine, autoflush=False, future=True)
    return _Session()
