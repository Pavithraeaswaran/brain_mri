import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_DIR = BASE_DIR / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'mri.db'}")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
