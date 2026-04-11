from pydantic import BaseModel, EmailStr, Field

#POST instituições
class InstitutionCreate(BaseModel):
    name: str

class InstitutionCreateResponse(BaseModel):
    id: int

    model_config = {
        "from_attributes": True
    }

#GET instituições
class InstitutionItem(BaseModel):
    id: int
    name: str

class InstitutionObtain(BaseModel):
    institutions: list[InstitutionItem]


#POST Alunos
class StudentCreate(BaseModel):
    email: EmailStr
    password: str

class StudentCreateResponse(BaseModel):
    id: int

    model_config = {
        "from_attributes": True
    }

#GET Alunos
class StudentItem(BaseModel):
    id: int
    email: str

class StudentByInstitution(BaseModel):
    total: int = Field(description="Total amount of entries returned to this institution")
    limit: int = Field(description="Amount of entries to be returned")
    page: int = Field(description="Determines the offset of the query. Determined by the limit: limit*(page-1).")
    students: list[StudentItem]