from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user, require_admin
import models, schemas

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=schemas.UserListResponse)
def list_users(
    db: Session     = Depends(get_db),
    _:  models.User = Depends(require_admin),
):
    """[Admin] Daftar semua user."""
    users = db.query(models.User).order_by(models.User.id).all()
    return schemas.UserListResponse(total=len(users), users=users)


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    """Data user yang sedang login (alias /auth/me)."""
    return current_user


@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(
    user_id: int,
    db:      Session     = Depends(get_db),
    _:       models.User = Depends(require_admin),
):
    """[Admin] Detail satu user."""
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id:      int,
    db:           Session     = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """[Admin] Hapus user (cascade ke orders & recommendations)."""
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tidak bisa menghapus akun sendiri")

    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan")

    db.delete(user)
    db.commit()
