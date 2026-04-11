from pydantic import BaseModel, EmailStr

class InstitutionCreate(BaseModel):
    nome: str

class InstitutionCreateResponse(BaseModel):
    id: int

    model_config = {
        "from_attributes": True
    }

class InstitutionItem(BaseModel):
    id: int
    name: str

class InstitutionObtain(BaseModel):
    isntitutions: list[InstitutionItem]


class StudentCreate(BaseModel):
    email: EmailStr
    password: str

class StudentCreateResponse(BaseModel):
    id: int

    model_config = {
        "from_attributes": True
    }