from fastapi import Cookie, HTTPException
from typing import Annotated
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv()

ACCESS_SECRET_KEY = os.getenv("ACCESS_SECRET_KEY")

async def validate_access_token(access_token: Annotated[str | None, Cookie()] = None):
    if access_token is None:
        raise HTTPException(status_code=401, detail="Token de acesso não informado")
    try:
        payload = jwt.decode(access_token, ACCESS_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expirado")

async def validate_professor(access_token: Annotated[str | None, Cookie()] = None):
    if access_token is None:
        raise HTTPException(status_code=401, detail="Token de acesso não informado")
    try:
        payload = jwt.decode(access_token, ACCESS_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    if payload.get("role") != "professor":
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

async def validate_student(access_token: Annotated[str | None, Cookie()] = None):
    if access_token is None:
        raise HTTPException(status_code=401, detail="Token de acesso não informado")
    try:
        payload = jwt.decode(access_token, ACCESS_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    if payload.get("role") != "student":
        raise HTTPException(status_code=403, detail="Usuário não autorizado")