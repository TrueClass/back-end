from . import service, schemas
from app.core.database import get_redis, get_db
from app.core.cookies import set_access_cookie, clear_auth_cookies
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response

router = APIRouter(prefix="/authenticate", tags=["Autenticação"])

@router.get("", response_model=schemas.AuthenticateResponse, status_code=200)
async def authenticate_request(
    response: Response,
    refresh_token: str = Cookie(None),
    cache = Depends(get_redis),
    db = Depends(get_db)
):
    try:
        new_access_token = await service.is_token_valid(refresh_token, cache, db)
    except service.TokenNotRecieved:
        raise HTTPException(status_code=401, detail="Token não informado na requisição")
    except service.TokenNotActive:
        raise HTTPException(status_code=401, detail="Sessão encerrada ou expirada")
    except service.InvalidOrInaccessibleToken:
        raise HTTPException(status_code=401, detail="Token inválido")

    set_access_cookie(response, new_access_token)
    return { "message": "Autenticação realizada com sucesso!"}

@router.delete("", response_model=schemas.AuthenticateResponse, status_code=200)
async def logout_request(
    response: Response,
    refresh_token: str = Cookie(None),
    cache = Depends(get_redis)
):
    try:
        await service.logout(refresh_token, cache)
    except (service.TokenNotRecieved, service.InvalidOrInaccessibleToken):
        pass
    clear_auth_cookies(response)
    return {"message": "Logout realizado com sucesso"}
