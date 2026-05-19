from pydantic import BaseModel, EmailStr, Field

class StudentCreate(BaseModel):
    email: EmailStr
    password: str

class StudentCreateResponse(BaseModel):
    id: int

    model_config = {
        "from_attributes": True
    }

class StudentItem(BaseModel):
    id: int
    email: EmailStr

class StudentByInstitution(BaseModel):
    total: int = Field(description="Total amount of entries returned to this institution")
    limit: int = Field(description="Amount of entries to be returned")
    page: int = Field(description="Determines the offset of the query. Determined by the limit: limit*(page-1).")
    students: list[StudentItem]
