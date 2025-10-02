from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, List

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TaskResponse(BaseModel):
    id: int
    filename: str
    status: str
    bbox: Optional[Dict] = None
    address: Optional[str] = None
    # ИЗМЕНИЛ metadata на image_metadata
    image_metadata: Optional[Dict] = None
    download_url: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SearchRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    radius_km: float = 1.0
    time_interval_years: int = 3
    source_filter: str = "all"
    min_resolution: Optional[str] = None
    min_score: float = 0.5
    search_principle: str = "radius"

class SearchHistoryResponse(BaseModel):
    id: int
    query_type: str
    params: Dict
    results_count: int
    created_at: datetime

    class Config:
        from_attributes = True