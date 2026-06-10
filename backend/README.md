# Sakka Base NCF — Backend

FastAPI backend untuk sistem rekomendasi menu Neural Collaborative Filtering.

## Setup

### 1. Masuk ke folder backend
```bash
cd backend
```

### 2. Install dependensi
```bash
python -m pip install -r requirements.txt
```

### 3. Buat file .env
```bash
copy .env.example .env
```
Edit `.env` sesuai konfigurasi MySQL lokal kamu.

### 4. Jalankan server
```bash
uvicorn main:app --reload
```

Server berjalan di: http://localhost:8000

Health check: http://localhost:8000/health

API docs (Swagger): http://localhost:8000/docs

## Struktur folder

```
backend/
├── main.py         — entry point FastAPI
├── config.py       — konfigurasi dari .env
├── database.py     — SQLAlchemy engine & session
├── .env            — konfigurasi lokal (tidak di-commit)
├── .env.example    — template .env
└── requirements.txt
```
