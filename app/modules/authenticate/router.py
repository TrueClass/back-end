from . import service, schemas
from app.core.database import get_redis, get_db
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response

router = APIRouter(prefix="/authenticate", tags=["Autenticação"])

@router.get("/",response_model= schemas.AuthenticateResponse, status_code=200)
async def authenticate_request( 
    refresh_token: str = Cookie(None), 
    cache = Depends(get_redis),
    db = Depends(get_db)
):
    try:
        new_access_token = await service.is_token_valid(refresh_token, cache, db)
        if(new_access_token):
            return {"access_token" : new_access_token, "token_type" : "bearer" }
    except service.TokenNotRecieved:
        raise HTTPException(status_code=401, detail="Token wasn't informed on request.")
    except service.TokenNotActive:
        raise HTTPException(status_code=401, detail="Token isn't active on database")
    except service.InvalidOrInaccessibleToken:
        raise HTTPException(status_code=401, detail="Token is unreachable or doesn't exist")
