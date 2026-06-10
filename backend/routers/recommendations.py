from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user, require_admin
import models, schemas

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


def _popularity_fallback(db: Session, limit: int = 10) -> list[schemas.RecommendationItem]:
    """
    Cold-start fallback: Top-N menu berdasarkan frekuensi pemesanan terbanyak.
    Digunakan ketika user belum memiliki rekomendasi NCF di database.
    """
    rows = (
        db.query(models.MenuItem, func.count(models.OrderDetail.id).label("cnt"))
        .join(models.OrderDetail, models.OrderDetail.menu_item_id == models.MenuItem.id)
        .group_by(models.MenuItem.id)
        .order_by(func.count(models.OrderDetail.id).desc())
        .limit(limit)
        .all()
    )
    max_cnt = rows[0][1] if rows else 1
    return [
        schemas.RecommendationItem(
            rank      = rank + 1,
            score     = round(float(cnt) / max_cnt, 4),
            menu_item = item,
        )
        for rank, (item, cnt) in enumerate(rows)
    ]


@router.get("/me", response_model=schemas.RecommendationResponse)
def my_recommendations(
    db:           Session     = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Top-10 rekomendasi untuk user yang sedang login.
    Jika belum ada rekomendasi NCF (cold-start), kembalikan popularity-based Top-10.
    """
    recs = (
        db.query(models.Recommendation)
        .filter(models.Recommendation.user_id == current_user.id)
        .order_by(models.Recommendation.rank)
        .all()
    )

    if recs:
        items = [
            schemas.RecommendationItem(rank=r.rank, score=r.score, menu_item=r.menu_item)
            for r in recs
        ]
    else:
        items = _popularity_fallback(db)

    return schemas.RecommendationResponse(user_id=current_user.id, items=items)


@router.get("/{user_id}", response_model=schemas.RecommendationResponse)
def get_recommendations(
    user_id: int,
    db:      Session     = Depends(get_db),
    _:       models.User = Depends(require_admin),
):
    """[Admin] Top-10 rekomendasi untuk user tertentu (dengan cold-start fallback)."""
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan")

    recs = (
        db.query(models.Recommendation)
        .filter(models.Recommendation.user_id == user_id)
        .order_by(models.Recommendation.rank)
        .all()
    )

    if recs:
        items = [
            schemas.RecommendationItem(rank=r.rank, score=r.score, menu_item=r.menu_item)
            for r in recs
        ]
    else:
        items = _popularity_fallback(db)

    return schemas.RecommendationResponse(user_id=user_id, items=items)
