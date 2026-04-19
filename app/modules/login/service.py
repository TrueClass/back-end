from jose import jwt
from argon2 import verify_password, Type
from datetime import datetime, timedelta, timezone
from .models import LOGIN_SELECT_PROFESSOR_QUERY, LOGIN_SELECT_STUDENT_QUERY
from dotenv import load_dotenv
from uuid import uuid4
import os

load_dotenv()
ACCESS_SECRET_KEY = os.getenv("ACCESS_SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")

async def authenticate_user(data: object, db, cache) -> object:
    """
    Consume a login info sent from a POST API request, authenticate it, and return a JWT (JSON Web Token).
    """
    cursor = db.cursor(dictionary=True)
    values = (data.email,)

    # Search for a professor
    cursor.execute(LOGIN_SELECT_PROFESSOR_QUERY,values)
    user = cursor.fetchone()
    user_type = "professor"

    # If it isn't a professor, search for a student
    if not user:
        cursor.execute(LOGIN_SELECT_STUDENT_QUERY, values)
        user = cursor.fetchone()
        user_type = "student"
    
    # If the user doesn't exist
    if not user:
        raise IncorrectUserOrPassword()
    
    # Check if the password is right and create data to return
    if verify_password(
        user["password_hash"].encode('utf-8'), 
        data.password.encode('utf-8'), 
        Type.ID):
        
        user.update({"role" : user_type})
        user_id = str(user["id"])
        sub_data = {
            "sub" : user_id
        }

        access_token = create_access_token(sub_data.copy(),user)
        refresh_token, jti = create_refresh_token(sub_data.copy())

        #TrueClass:Refresh:User_id:Token
        await cache.set(f"tc:ref:{user_id}:{jti}", "active", ex=604800)

        return (access_token, refresh_token)
    
    # Returns None if user missed his password
    raise IncorrectUserOrPassword()

def create_access_token(to_encode: object, user: object) -> object:
    expire = int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp())
    iat = int(datetime.now(timezone.utc).timestamp())

    to_encode.update({
        "email" : user["email"],
        "type" : "access",
        "exp" : expire,
        "iat" : iat,
        "role" : user["role"]
    })

    token = jwt.encode(to_encode, ACCESS_SECRET_KEY, algorithm="HS256")
    return token

def create_refresh_token(to_encode: object) -> object:
    expire = int((datetime.now(timezone.utc) + timedelta(days=7)).timestamp())
    jti = str(uuid4())

    to_encode.update({
        "type" : "refresh",
        "jti" : jti,
        "exp" : expire
    })

    token = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm="HS256")
    return token, jti

class IncorrectUserOrPassword(Exception):
    """Raised when user is not found OR he missed his password"""
    pass