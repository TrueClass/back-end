from fastapi import APIRouter, Depends, HTTPException, Cookie, Response
from app.core.database import get_redis
from . import service

router = APIRouter(prefix="/authenticate", tags=["Autenticação"])

@router.get("/")
async def authenticate_request(
    refresh_token: str = Cookie(None), 
    cache = Depends(get_redis)
):
    try:
        if(await service.is_token_valid(refresh_token, cache)):
            return Response(status_code=200)
    except service.TokenNotRecieved:
        raise HTTPException(status_code=401, detail="Token wasn't informed on request.")
    except service.TokenNotActive:
        raise HTTPException(status_code=401, detail="Token isn't active on database")
    except service.InvalidOrInaccessibleToken:
        raise HTTPException(status_code=401, detail="Token is unreachable or doesn't exist")
