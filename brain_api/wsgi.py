from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .settings import MEDIA_DIR, CORS_ORIGINS
from backend.mri_app.urls import api_router

app = FastAPI(title="Brain MRI API", version="1.0.0")

# CORS
origins = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]
if not origins:
    origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static media mount
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

# Include API routes
app.include_router(api_router, prefix="/api")

# Health check
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
