from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String, unique=True, index=True)
    filename = Column(String)
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow)
    image_url = Column(String)
    prediction = Column(String)
    confidence = Column(Float)
    format = Column(String)
    dimensions = Column(String)
