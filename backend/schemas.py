"""
Pydantic schemas untuk validasi request dan serialisasi response.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, field_validator


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type:   str = "bearer"

class TokenData(BaseModel):
    user_id:  int
    username: str
    role:     str


# ── User ──────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    nama_lengkap: str
    username:     str
    password:     str

class UserResponse(BaseModel):
    id:           int
    nama_lengkap: str
    username:     str
    role:         str
    source:       str
    created_at:   datetime

    model_config = {"from_attributes": True}

class UserListResponse(BaseModel):
    total: int
    users: list[UserResponse]


# ── MenuItem ──────────────────────────────────────────────────────────────────

class MenuItemResponse(BaseModel):
    id:        int
    item_id:   str
    nama_menu: str
    kategori:  str

    model_config = {"from_attributes": True}

class MenuItemListResponse(BaseModel):
    total: int
    items: list[MenuItemResponse]


# ── Order ─────────────────────────────────────────────────────────────────────

class OrderResponse(BaseModel):
    id:        int
    user_id:   int
    tanggal:   date
    menu_item: MenuItemResponse

    model_config = {"from_attributes": True}

class OrderListResponse(BaseModel):
    total:  int
    orders: list[OrderResponse]


# ── Recommendation ────────────────────────────────────────────────────────────

class RecommendationItem(BaseModel):
    rank:      int
    score:     float
    menu_item: MenuItemResponse

    model_config = {"from_attributes": True}

class RecommendationResponse(BaseModel):
    user_id: int
    items:   list[RecommendationItem]


# ── Model Status ──────────────────────────────────────────────────────────────

class ModelStatusResponse(BaseModel):
    id:         int
    status:     str
    model_path: str
    hr_at_10:   Optional[float]
    ndcg_at_10: Optional[float]
    trained_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
