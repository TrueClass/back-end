from fastapi import APIRouter, Depends, HTTPException, Response
from app.core.database import get_db, get_redis
from . import service, schemas

# Criando uma instância do APIRouter, prefix diz que a todas as rotas começam com students e tags 
router = APIRouter(prefix="/login", tags=["Login"])

@router.post("/", response_model=schemas.LoginResponse, status_code=200)
async def login(response: Response, login_in: schemas.Login, db = Depends(get_db), cache = Depends(get_redis)):
    try:
        login_data = await service.authenticate_user(login_in, db, cache)

        response.set_cookie(
            key="refresh_token",
            value=login_data[1],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=604800 # Tempo de vida em segundos (7 dias)
        )
        
        return {"access_token" : login_data[0], "token_type" : "bearer" }
    except service.IncorrectUserOrPassword:
        raise HTTPException(status_code=401, detail="Usuário ou senha incorreta")