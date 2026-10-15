from fastapi import APIRouter, Depends, HTTPException, Response
from app.core.database import get_db, get_redis
from app.core.cookies import set_access_cookie, set_refresh_cookie
from . import service, schemas

# Criando uma instância do APIRouter, prefix diz que a todas as rotas começam com students e tags
router = APIRouter(prefix="/login", tags=["Login"])

@router.post("", response_model=schemas.LoginResponse, status_code=200)
async def login(response: Response, login_in: schemas.Login, db = Depends(get_db), cache = Depends(get_redis)):
    try:
        access_token, refresh_token = await service.authenticate_user(login_in, db, cache)
    except service.IncorrectUserOrPassword:
        raise HTTPException(status_code=401, detail="Usuário ou senha incorreta")

    set_access_cookie(response, access_token)
    set_refresh_cookie(response, refresh_token)
    return { "message" : "Login realizado com sucesso!"}
