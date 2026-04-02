from datetime import datetime
from pydantic import BaseModel, EmailStr
# O que recebemos pelo POST
class Login(BaseModel):
    email: EmailStr
    password: str

# Resposta ao POST
class LoginResponse(BaseModel):
    access_token: str
    token_type: str

    model_config = {
        "from_attributes": True
    }