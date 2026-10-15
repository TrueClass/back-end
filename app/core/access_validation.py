from fastapi import Cookie, Depends, Header, HTTPException
from typing import Annotated
from jose import jwt, JWTError
from dotenv import load_dotenv
import hmac
import os

load_dotenv()

ACCESS_SECRET_KEY = os.getenv("ACCESS_SECRET_KEY")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

async def validate_access_token(access_token: Annotated[str | None, Cookie()] = None) -> dict:
    if access_token is None:
        raise HTTPException(status_code=401, detail="Token de acesso não informado")
    try:
        payload = jwt.decode(access_token, ACCESS_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    if payload.get("type") != "access" or "sub" not in payload or "inst" not in payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    return payload

def require_role(*roles: str):
    async def dependency(payload: dict = Depends(validate_access_token)) -> dict:
        if payload.get("role") not in roles:
            raise HTTPException(status_code=403, detail="Usuário não autorizado")
        return payload
    return dependency

validate_professor = require_role("professor")
validate_student = require_role("student")

async def validate_coordinator(payload: dict = Depends(validate_professor)) -> dict:
    if not payload.get("coord"):
        raise HTTPException(status_code=403, detail="Usuário não autorizado")
    return payload

async def validate_institution_member(institution_id: int, payload: dict = Depends(validate_access_token)) -> dict:
    if payload.get("inst") != institution_id:
        raise HTTPException(status_code=403, detail="Usuário não pertence a esta instituição")
    return payload

def is_admin_key_valid(x_admin_key: str | None) -> bool:
    if not ADMIN_API_KEY or not x_admin_key:
        return False
    return hmac.compare_digest(x_admin_key, ADMIN_API_KEY)

async def validate_admin(x_admin_key: Annotated[str | None, Header()] = None):
    if not is_admin_key_valid(x_admin_key):
        raise HTTPException(status_code=403, detail="Usuário não autorizado")
