from jose import jwt
from argon2.exceptions import VerificationError, InvalidHashError
from datetime import datetime, timedelta, timezone
from app.core.security import password_hasher, DUMMY_HASH
from app.core.cookies import REFRESH_TOKEN_MAX_AGE
from .models import LOGIN_SELECT_USER_QUERY, LOGIN_SELECT_USER_BY_ID_QUERY, UPDATE_PASSWORD_HASH_QUERY
from dotenv import load_dotenv
from uuid import uuid4
import os

load_dotenv()
ACCESS_SECRET_KEY = os.getenv("ACCESS_SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")

async def authenticate_user(data: object, db, cache) -> tuple[str, str]:
    """
    Consume a login info sent from a POST API request, authenticate it, and return a JWT (JSON Web Token).
    """
    user = fetch_user_info(data.email, db)

    password_hash = user["password_hash"] if user else DUMMY_HASH
    try:
        password_hasher.verify(password_hash, data.password)
    except (VerificationError, InvalidHashError):
        raise IncorrectUserOrPassword()

    if not user:
        raise IncorrectUserOrPassword()

    if password_hasher.check_needs_rehash(password_hash):
        rehash_password(user["id"], data.password, db)

    access_token = create_access_token(user)
    refresh_token, jti = create_refresh_token(user)

    #TrueClass:Refresh:User_id:Token
    await cache.set(f"tc:ref:{user['id']}:{jti}", "active", ex=REFRESH_TOKEN_MAX_AGE)

    return (access_token, refresh_token)

def fetch_user_info(email: str, db) -> dict | None:
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(LOGIN_SELECT_USER_QUERY, (email,))
        return cursor.fetchone()
    finally:
        cursor.close()

def fetch_user_by_id(user_id: int, db) -> dict:
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(LOGIN_SELECT_USER_BY_ID_QUERY, (user_id,))
        user = cursor.fetchone()
    finally:
        cursor.close()

    if not user:
        raise UserNotFoundError()

    return user

def rehash_password(user_id: int, password: str, db):
    cursor = db.cursor()
    try:
        cursor.execute(UPDATE_PASSWORD_HASH_QUERY, (password_hasher.hash(password), user_id))
        db.commit()
    finally:
        cursor.close()

def create_access_token(user: dict) -> str:
    now = datetime.now(timezone.utc)

    to_encode = {
        "sub" : str(user["id"]),
        "role" : user["role"],
        "inst" : user["institution_id"],
        "coord" : bool(user["is_coordinator"]),
        "type" : "access",
        "exp" : int((now + timedelta(minutes=30)).timestamp()),
        "iat" : int(now.timestamp())
    }

    return jwt.encode(to_encode, ACCESS_SECRET_KEY, algorithm="HS256")

def create_refresh_token(user: dict) -> tuple[str, str]:
    expire = int((datetime.now(timezone.utc) + timedelta(days=7)).timestamp())
    jti = str(uuid4())

    to_encode = {
        "sub" : str(user["id"]),
        "type" : "refresh",
        "jti" : jti,
        "exp" : expire
    }

    token = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm="HS256")
    return token, jti

class IncorrectUserOrPassword(Exception):
    """Raised when user is not found OR he missed his password"""
    pass

class UserNotFoundError(Exception):
    """Raised when the user id inside a token no longer exists"""
    pass
