from ..login.service import fetch_user_info, create_access_token
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv()

REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")

async def is_token_valid(refresh_token, cache, db):
    if not refresh_token:
        raise TokenNotRecieved()

    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        raise InvalidOrInaccessibleToken()

    jti = payload.get("jti")
    user_email = payload.get("sub")

    status = await cache.get(f"tc:ref:{user_email}:{jti}")
    if status != "active":
        raise TokenNotActive()

    user = fetch_user_info(user_email, db)
    return create_access_token(user)

async def logout(refresh_token, cache):
    if not refresh_token:
        raise TokenNotRecieved()

    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        raise InvalidOrInaccessibleToken()

    jti = payload.get("jti")
    user_email = payload.get("sub")
    await cache.delete(f"tc:ref:{user_email}:{jti}")
 
class TokenNotRecieved(Exception):
    """Raised when there's not an token in the request"""
    pass

class TokenNotActive(Exception):
    """Raised when token is not active on Redis"""
    pass

class InvalidOrInaccessibleToken(Exception):
    """Raised when token is invalid, or isn't found on Redis"""
    pass