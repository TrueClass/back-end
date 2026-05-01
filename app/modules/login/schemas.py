from pydantic import BaseModel, EmailStr

# O que recebemos pelo POST
class Login(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    message: str