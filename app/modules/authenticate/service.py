from ..login.service import fetch_user_info, create_access_token
from jose import jwt
from dotenv import load_dotenv
import os

load_dotenv()

REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")

async def is_token_valid(refresh_token, cache, db):
    if not refresh_token:
        raise TokenNotRecieved()

    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=["HS256"])
        jti = payload.get("jti")
        user_email = payload.get("sub")

        # 2. Verifica no Redis se o JTI ainda é válido (não foi deslogado)
        status = await cache.get(f"tc:ref:{user_email}:{jti}")
        
        if status != "active":
            raise TokenNotActive()
        
        user = fetch_user_info(user_email, db)
        new_access_token = create_access_token(user)

        # Se chegou aqui, retorna 200 OK e o Nginx libera o acesso
        return new_access_token # Response(status_code=200)
    except:
        raise InvalidOrInaccessibleToken()
 
class TokenNotRecieved(Exception):
    """Raised when there's not an token in the request"""
    pass

class TokenNotActive(Exception):
    """Raised when token is not active on Redis"""
    pass

class InvalidOrInaccessibleToken(Exception):
    """Raised when token is invalid, or isn't found on Redis"""
    pass