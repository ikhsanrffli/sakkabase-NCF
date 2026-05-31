from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.database import get_db

app = FastAPI(
    title="Sakka Base NCF API",
    description="Backend sistem rekomendasi menu Neural Collaborative Filtering",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """Cek status API dan koneksi database."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"

    return {
        "status": "ok",
        "service": "sakkabase-ncf-api",
        "database": db_status,
    }
