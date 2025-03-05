from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/")
def get_status_root():
    return {"message": "Status endpoint root"}

@router.get("/{user_id}")
def get_status(user_id: str):
    status = "not started" 
    return {"user_id": user_id, "status": status}

@router.get("/error")
def error_route():
    raise HTTPException(status_code=500, detail="Intentional Error")
