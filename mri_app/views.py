import os
import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi import Depends
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker, Session
from PIL import Image

from backend.brain_api.settings import MEDIA_DIR, DB_URL
from .models import Base, Scan
from .serializers import ScanOut, AnalyticsOut, Metadata
from .inference import get_model

# Database setup
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="", tags=["mri"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload", response_model=ScanOut)
async def upload_mri(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Validate content type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    # Save file to media directory
    scan_id = uuid.uuid4().hex[:9]
    name, ext = os.path.splitext(file.filename)
    safe_name = f"{scan_id}{ext.lower()}"
    out_path = MEDIA_DIR / safe_name

    # Write file
    content = await file.read()
    with open(out_path, "wb") as f:
        f.write(content)

    # Get image metadata
    try:
        with Image.open(out_path) as img:
            width, height = img.size
            dimensions = f"{width}x{height}"
            fmt = img.format
    except Exception:
        dimensions = ""
        fmt = file.content_type

    # Run inference
    model = get_model()
    result = model.predict(str(out_path))

    # Persist to DB
    scan = Scan(
        scan_id=scan_id,
        filename=file.filename,
        file_size=len(content),
        upload_date=datetime.utcnow(),
        image_url=f"/media/{safe_name}",
        prediction=result.prediction,
        confidence=float(result.confidence),
        format=str(fmt),
        dimensions=dimensions,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    return ScanOut(
        id=scan.scan_id,
        filename=scan.filename,
        fileSize=scan.file_size,
        uploadDate=scan.upload_date,
        imageUrl=scan.image_url,
        prediction=scan.prediction,
        confidence=scan.confidence,
        processed=True,
        metadata=Metadata(
            dimensions=scan.dimensions or "",
            format=scan.format or "",
            size=f"{round(scan.file_size/1024,1)} KB",
        ),
    )

@router.get("/scans", response_model=List[ScanOut])
async def list_scans(db: Session = Depends(get_db)):
    scans = db.execute(select(Scan).order_by(Scan.upload_date.desc())).scalars().all()
    return [
        ScanOut(
            id=s.scan_id,
            filename=s.filename,
            fileSize=s.file_size,
            uploadDate=s.upload_date,
            imageUrl=s.image_url,
            prediction=s.prediction,
            confidence=s.confidence,
            processed=True,
            metadata=Metadata(
                dimensions=s.dimensions or "",
                format=s.format or "",
                size=f"{round(s.file_size/1024,1)} KB",
            ),
        ) for s in scans
    ]

@router.get("/scans/{scan_id}", response_model=ScanOut)
async def get_scan(scan_id: str, db: Session = Depends(get_db)):
    s = db.execute(select(Scan).where(Scan.scan_id == scan_id)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Scan not found")
    return ScanOut(
        id=s.scan_id,
        filename=s.filename,
        fileSize=s.file_size,
        uploadDate=s.upload_date,
        imageUrl=s.image_url,
        prediction=s.prediction,
        confidence=s.confidence,
        processed=True,
        metadata=Metadata(
            dimensions=s.dimensions or "",
            format=s.format or "",
            size=f"{round(s.file_size/1024,1)} KB",
        ),
    )

@router.get("/analytics", response_model=AnalyticsOut)
async def analytics(db: Session = Depends(get_db)):
    total = db.execute(select(func.count(Scan.id))).scalar() or 0
    tumor = db.execute(select(func.count(Scan.id)).where(Scan.prediction == "Tumor")).scalar() or 0
    normal = total - tumor
    accuracy = round(((normal + tumor) / total * 100) if total > 0 else 0, 1)
    return AnalyticsOut(
        totalScans=total,
        tumorDetected=tumor,
        normalScans=normal,
        accuracy=accuracy,
    )
