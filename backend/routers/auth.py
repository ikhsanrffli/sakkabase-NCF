from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth import hash_password, verify_password, create_access_token, get_current_user
import models
import schemas

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=schemas.Token)
def login(body: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Login untuk Admin dan User terdaftar.
    User historical (source=historical) tidak bisa login karena password NULL.
    """
    user = db.query(models.User).filter(models.User.username == body.username).first()

    if not user or not user.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username atau password salah")

    if not verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username atau password salah")

    token = create_access_token(schemas.TokenData(
        user_id  = user.id,
        username = user.username,
        role     = user.role,
    ))
    return schemas.Token(access_token=token)


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(body: schemas.UserRegister, db: Session = Depends(get_db)):
    """Registrasi user baru (source=registered, role=user)."""
    existing = db.query(models.User).filter(models.User.username == body.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username sudah digunakan")

    user = models.User(
        nama_lengkap = body.nama_lengkap,
        username     = body.username,
        password     = hash_password(body.password),
        role         = "user",
        source       = "registered",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=schemas.UserResponse)
def me(current_user: models.User = Depends(get_current_user)):
    """Kembalikan data user yang sedang login."""
    return current_user
