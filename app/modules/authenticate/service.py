from ..login.service import fetch_user_by_id, create_access_token, UserNotFoundError
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv()

REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")

def decode_refresh_token(refresh_token) -> dict:
    if not refresh_token:
        raise TokenNotRecieved()

    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        raise InvalidOrInaccessibleToken()

    if payload.get("type") != "refresh" or not payload.get("sub") or not payload.get("jti"):
        raise InvalidOrInaccessibleToken()
    return payload

async def is_token_valid(refresh_token, cache, db):
    payload = decode_refresh_token(refresh_token)
    key = f"tc:ref:{payload['sub']}:{payload['jti']}"

    status = await cache.get(key)
    if status != "active":
        raise TokenNotActive()

    try:
        user = fetch_user_by_id(int(payload["sub"]), db)
    except UserNotFoundError:
        await cache.delete(key)
        raise TokenNotActive()

    return create_access_token(user)

async def logout(refresh_token, cache):
    payload = decode_refresh_token(refresh_token)
    await cache.delete(f"tc:ref:{payload['sub']}:{payload['jti']}")

class TokenNotRecieved(Exception):
    """Raised when there's not an token in the request"""
    pass

class TokenNotActive(Exception):
    """Raised when token is not active on Redis"""
    pass

class InvalidOrInaccessibleToken(Exception):
    """Raised when token is invalid, or isn't found on Redis"""
    pass
