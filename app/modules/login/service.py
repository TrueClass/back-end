from jose import jwt
from argon2 import verify_password
from datetime import datetime, timedelta, timezone
from .models import LOGIN_SELECT_PROFESSOR_QUERY, LOGIN_SELECT_STUDENT_QUERY
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

def authenticate_user(data: object, db) -> object:
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
        return None
    
    # Check if the password is right and create data to return
    if verify_password(user["password_hash"], data.password):
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        expire = int(expire.timestamp())
        now = datetime.now(timezone.utc)
        iat = int(now.timestamp())
        to_encode = {
            "sub" : str(user["id"]),
            "email" : user["email"],
            "role" : user_type,
            "exp" : expire,
            "iat" : iat
        }
        token = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

        return token
    
    # Returns None if user missed his password
    return None