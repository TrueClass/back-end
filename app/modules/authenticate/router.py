from . import service, schemas
from app.core.database import get_redis, get_db
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response

router = APIRouter(prefix="/authenticate", tags=["Autenticação"])

@router.get("/", response_model=schemas.AuthenticateResponse, status_code=200)
async def authenticate_request(
    response: Response,
    refresh_token: str = Cookie(None),
    cache = Depends(get_redis),
    db = Depends(get_db)
):
    try:
        new_access_token = await service.is_token_valid(refresh_token, cache, db)
        if(new_access_token):
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=3600 # Tempo de vida em segundos (1 hora)
            )
        return { "message":"Authentication has been made successfully!"}
    except service.TokenNotRecieved:
        raise HTTPException(status_code=401, detail="Token wasn't informed on request.")
    except service.TokenNotActive:
        raise HTTPException(status_code=401, detail="Token isn't active on database")
    except service.InvalidOrInaccessibleToken:
        raise HTTPException(status_code=401, detail="Token is unreachable or doesn't exist")

@router.delete("/", response_model=schemas.AuthenticateResponse, status_code=200)
async def logout_request(
    response: Response,
    refresh_token: str = Cookie(None),
    cache = Depends(get_redis)
):
    try:
        await service.logout(refresh_token, cache)
    except (service.TokenNotRecieved, service.InvalidOrInaccessibleToken):
        pass
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}
