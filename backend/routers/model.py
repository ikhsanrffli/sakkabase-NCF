import os
import sys
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Tambah root project ke path agar ncf module bisa diimport
# __file__ = backend/routers/model.py → 3x dirname = project root (sakkabase-NCF/)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db, SessionLocal
from auth import require_admin
from config import settings
import models, schemas

router = APIRouter(prefix="/model", tags=["Model"])


# ── Background retrain task ───────────────────────────────────────────────────

def _retrain_background(status_id: int) -> None:
    """
    Dijalankan sebagai background task:
    1. Latih ulang model NCF
    2. Perbarui model_status dengan metrik hasil
    3. Generate rekomendasi baru untuk semua user yang punya riwayat order
    """
    from ncf.train import train
    from ncf.predict import recommend, save_recommendations
    from ncf.config import MODEL_PATH

    db = SessionLocal()
    try:
        # Latih model
        result = train(model_path=MODEL_PATH, save_plot=False, verbose=False)

        # Perbarui status → ready
        record = db.get(models.ModelStatus, status_id)
        record.status     = "ready"
        record.hr_at_10   = result["best_hr"]
        record.ndcg_at_10 = result["best_ndcg"]
        record.trained_at = datetime.now()
        db.commit()

        # Generate rekomendasi untuk semua user yang punya order
        user_ids = [
            row[0] for row in
            db.query(models.Order.user_id).distinct().all()
        ]
        for uid in user_ids:
            recs = recommend(uid, model_path=MODEL_PATH)
            if recs:
                save_recommendations(uid, recs)

    except Exception as exc:
        record = db.get(models.ModelStatus, status_id)
        if record:
            record.status    = "error"
            record.error_log = str(exc)
            db.commit()
    finally:
        db.close()


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/retrain", status_code=status.HTTP_202_ACCEPTED)
def retrain(
    background_tasks: BackgroundTasks,
    db:               Session     = Depends(get_db),
    _:                models.User = Depends(require_admin),
):
    """
    [Admin] Trigger retrain model NCF (berjalan di background).
    Kembalikan id record model_status yang bisa dipantau via GET /model/status.
    """
    # Cek apakah sedang ada training yang berjalan
    ongoing = (
        db.query(models.ModelStatus)
        .filter(models.ModelStatus.status == "training")
        .first()
    )
    if ongoing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Training sedang berjalan, tunggu hingga selesai",
        )

    record = models.ModelStatus(
        status     = "training",
        model_path = settings.MODEL_PATH,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    background_tasks.add_task(_retrain_background, record.id)

    return {"message": "Retrain dimulai", "status_id": record.id}


@router.get("/status", response_model=schemas.ModelStatusResponse)
def get_status(
    db: Session     = Depends(get_db),
    _:  models.User = Depends(require_admin),
):
    """[Admin] Status model NCF terbaru."""
    record = (
        db.query(models.ModelStatus)
        .order_by(models.ModelStatus.id.desc())
        .first()
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Belum ada data model")
    return record


@router.get("/status/all", response_model=list[schemas.ModelStatusResponse])
def get_all_status(
    db: Session     = Depends(get_db),
    _:  models.User = Depends(require_admin),
):
    """[Admin] Riwayat lengkap semua sesi training."""
    return db.query(models.ModelStatus).order_by(models.ModelStatus.id.desc()).all()
