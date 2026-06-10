from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user, require_admin
import models, schemas

router = APIRouter(prefix="/orders", tags=["Orders"])


class OrderCreate(BaseModel):
    items:   list[schemas.OrderItemCreate]
    tanggal: date = date.today()


@router.post("", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    body:         OrderCreate,
    db:           Session     = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Tambah pesanan baru (satu transaksi bisa punya beberapa item)."""
    if not body.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Items tidak boleh kosong")

    # Validasi semua menu dan hitung total
    details_data = []
    total = 0
    for item in body.items:
        menu_item = db.get(models.MenuItem, item.menu_item_id)
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu id={item.menu_item_id} tidak ditemukan",
            )
        subtotal = menu_item.price * item.qty
        total   += subtotal
        details_data.append((menu_item, item.qty, menu_item.price))

    # Buat header order
    order = models.Order(
        user_id = current_user.id,
        tanggal = body.tanggal,
        total   = total,
    )
    db.add(order)
    db.flush()  # dapatkan order.id sebelum commit

    # Buat detail order
    for menu_item, qty, price in details_data:
        detail = models.OrderDetail(
            order_id     = order.id,
            menu_item_id = menu_item.id,
            qty          = qty,
            price        = price,
        )
        db.add(detail)

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
