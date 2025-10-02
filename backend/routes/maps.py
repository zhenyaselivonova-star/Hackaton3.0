from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_map():
    return {"message": "Maps endpoint - to be implemented"}