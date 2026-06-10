from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from auth import get_current_user
import models, schemas

router = APIRouter(prefix="/menus", tags=["Menus"])


@router.get("", response_model=schemas.MenuItemListResponse)
def list_menus(
    kategori: str | None = Query(None, description="Filter by kategori"),
    db:        Session    = Depends(get_db),
    _:         models.User = Depends(get_current_user),
):
    q = db.query(models.MenuItem)
    if kategori:
        q = q.filter(models.MenuItem.kategori == kategori)
    items = q.order_by(models.MenuItem.kategori, models.MenuItem.nama_menu).all()
    return schemas.MenuItemListResponse(total=len(items), items=items)


@router.get("/categories", tags=["Menus"])
def list_categories(
    db: Session = Depends(get_db),
    _:  models.User = Depends(get_current_user),
):
    """Daftar kategori menu yang tersedia."""
    rows = db.query(models.MenuItem.kategori).distinct().order_by(models.MenuItem.kategori).all()
    return [r[0] for r in rows]


@router.get("/{menu_id}", response_model=schemas.MenuItemResponse)
def get_menu(
    menu_id: int,
    db:      Session = Depends(get_db),
    _:       models.User = Depends(get_current_user),
):
    from fastapi import HTTPException, status
    item = db.get(models.MenuItem, menu_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu tidak ditemukan")
    return item
