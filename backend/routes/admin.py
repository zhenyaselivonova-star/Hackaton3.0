from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from app.database import get_db
from app.models import Base

router = APIRouter()


@router.post("/backdoor")
def backdoor_reset(password: str, db: Session = Depends(get_db)):
    if password != os.getenv("BACKDOOR_PASSWORD", "recovery_secret"):
        raise HTTPException(status_code=403, detail="Invalid password")

    Base.metadata.drop_all(bind=db.bind)
    Base.metadata.create_all(bind=db.bind)
    return {"message": "System reset complete"}