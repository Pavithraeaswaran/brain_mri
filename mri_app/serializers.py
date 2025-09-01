from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class Metadata(BaseModel):
    dimensions: str
    format: str
    size: str

class ScanOut(BaseModel):
    id: str
    filename: str
    fileSize: int
    uploadDate: datetime
    imageUrl: str
    prediction: str
    confidence: float
    processed: bool = True
    metadata: Metadata

class ScanCreate(BaseModel):
    pass  # Placeholder if needed later

class AnalyticsOut(BaseModel):
    totalScans: int
    tumorDetected: int
    normalScans: int
    accuracy: float
