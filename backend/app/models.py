from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    original_filename = Column(String)
    storage_key = Column(String)
    status = Column(String, default="pending")
    bbox = Column(JSON)
    # ЗАМЕНИЛИ geometry на обычные float колонки
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String)
    image_metadata = Column(JSON)
    source = Column(String)
    resolution = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    user_id = Column(Integer, ForeignKey("users.id"))

class SearchHistory(Base):
    __tablename__ = "search_history"
    id = Column(Integer, primary_key=True, index=True)
    query_type = Column(String)
    params = Column(JSON)
    results_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
