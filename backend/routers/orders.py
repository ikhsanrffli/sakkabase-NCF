from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user, require_admin
import models, schemas

router = APIRouter(prefix="/orders", tags=["Orders"])


class OrderCreate(BaseModel):
    menu_item_id: int
    tanggal:      date = date.today()


@router.post("", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    body:         OrderCreate,
    db:           Session     = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Tambah pesanan baru untuk user yang sedang login."""
    menu_item = db.get(models.MenuItem, body.menu_item_id)
    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu tidak ditemukan")

    order = models.Order(
        user_id      = current_user.id,
        menu_item_id = body.menu_item_id,
        tanggal      = body.tanggal,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/my", response_model=schemas.OrderListResponse)
def my_orders(
    db:           Session     = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Riwayat pesanan milik user yang sedang login."""
    orders = (
        db.query(models.Order)
        .filter(models.Order.user_id == current_user.id)
        .order_by(models.Order.tanggal.desc())
        .all()
    )
    return schemas.OrderListResponse(total=len(orders), orders=orders)


@router.get("", response_model=schemas.OrderListResponse)
def list_orders(
    db: Session      = Depends(get_db),
    _:  models.User  = Depends(require_admin),
):
    """[Admin] Semua pesanan seluruh user."""
    orders = db.query(models.Order).order_by(models.Order.tanggal.desc()).all()
    return schemas.OrderListResponse(total=len(orders), orders=orders)
