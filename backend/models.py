"""
SQLAlchemy ORM models — mapping ke tabel yang sudah ada di MySQL.
reflect=True tidak dipakai agar struktur eksplisit dan mudah dibaca.
"""

from datetime import date, datetime
from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Float,
    Enum, Text, ForeignKey, func,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, index=True)
    nama_lengkap = Column(String(100), nullable=False)
    username     = Column(String(50),  nullable=False, unique=True, index=True)
    password     = Column(String(255), nullable=True)
    role         = Column(Enum("admin", "user"), nullable=False, default="user")
    source       = Column(Enum("historical", "registered"), nullable=False, default="registered")
    created_at   = Column(DateTime, nullable=False, server_default=func.now())

    orders          = relationship("Order",          back_populates="user", cascade="all, delete")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id         = Column(Integer,      primary_key=True, index=True)
    item_id    = Column(String(100),  nullable=False, unique=True, index=True)
    nama_menu  = Column(String(150),  nullable=False)
    kategori   = Column(String(100),  nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    orders          = relationship("Order",          back_populates="menu_item")
    recommendations = relationship("Recommendation", back_populates="menu_item", cascade="all, delete")


class Order(Base):
    __tablename__ = "orders"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id",      ondelete="CASCADE"),   nullable=False, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="RESTRICT"),  nullable=False, index=True)
    tanggal      = Column(Date,    nullable=False, index=True)
    created_at   = Column(DateTime, nullable=False, server_default=func.now())

    user      = relationship("User",     back_populates="orders")
    menu_item = relationship("MenuItem", back_populates="orders")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id",      ondelete="CASCADE"), nullable=False, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False, index=True)
    rank         = Column("rank", Integer,  nullable=False)
    score        = Column(Float,   nullable=False)
    generated_at = Column(DateTime, nullable=False, server_default=func.now())

    user      = relationship("User",     back_populates="recommendations")
    menu_item = relationship("MenuItem", back_populates="recommendations")


class ModelStatus(Base):
    __tablename__ = "model_status"

    id         = Column(Integer, primary_key=True, index=True)
    status     = Column(Enum("training", "ready", "error"), nullable=False, default="ready")
    model_path = Column(String(255), nullable=False)
    hr_at_10   = Column(Float,   nullable=True)
    ndcg_at_10 = Column(Float,   nullable=True)
    trained_at = Column(DateTime, nullable=True)
    error_log  = Column(Text,    nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
