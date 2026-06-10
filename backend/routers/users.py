from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user, require_admin, hash_password
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


@router.post("", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    body:         schemas.UserCreate,
    db:           Session     = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """[Admin] Tambah user baru dengan role pilihan."""
    existing = db.query(models.User).filter(models.User.username == body.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username sudah digunakan")

    if body.role not in ("admin", "user"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role harus 'admin' atau 'user'")

    user = models.User(
        nama_lengkap = body.nama_lengkap,
        username     = body.username,
        password     = hash_password(body.password),
        role         = body.role,
        source       = "registered",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id:      int,
    body:         schemas.UserUpdate,
    db:           Session     = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """[Admin] Edit data user (nama, username, password, role)."""
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan")

    if body.nama_lengkap is not None:
        user.nama_lengkap = body.nama_lengkap
    if body.username is not None:
        existing = db.query(models.User).filter(
            models.User.username == body.username,
            models.User.id != user_id,
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username sudah digunakan")
        user.username = body.username
    if body.password is not None and body.password.strip():
        user.password = hash_password(body.password)
    if body.role is not None:
        if body.role not in ("admin", "user"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role harus 'admin' atau 'user'")
        if user_id == current_user.id and body.role != "admin":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tidak bisa mengubah role akun sendiri")
        user.role = body.role

    db.commit()
    db.refresh(user)
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
