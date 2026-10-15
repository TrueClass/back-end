from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.core.access_validation import validate_access_token
from . import service, schemas

router = APIRouter(prefix="/me", tags=["Me"])

@router.get("", response_model=schemas.MeResponse, status_code=200)
async def get_me(token_data: dict = Depends(validate_access_token), db=Depends(get_db)):
    me = service.get_me(int(token_data["sub"]), db)
    if not me:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return me
