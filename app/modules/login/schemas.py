from pydantic import BaseModel, EmailStr, Field

# O que recebemos pelo POST
class Login(BaseModel):
    email: EmailStr
    password: str = Field(max_length=128)

class LoginResponse(BaseModel):
    message: str
