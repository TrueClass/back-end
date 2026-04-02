from datetime import datetime
from pydantic import BaseModel, EmailStr

# O que recebemos pelo POST
class StudentCreate(BaseModel):
    email: EmailStr
    password: str

# Resposta ao POST
class StudentCreateResponse(BaseModel):
    id: int

    model_config = {
        "from_attributes": True
    }