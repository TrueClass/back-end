from pydantic import BaseModel, EmailStr, Field

# --- POST institutions ---
class InstitutionCreate(BaseModel):
    name: str
    emails: list[str]

class InstitutionCreateResponse(BaseModel):
    id: int

    model_config = {
        "from_attributes": True
    }

# --- GET institutions ---
class InstitutionItem(BaseModel):
    id: int
    name: str
    emails: list[str]

class InstitutionObtain(BaseModel):
    institutions: list[InstitutionItem]

# --- POST students ---
class StudentCreate(BaseModel):
    email: EmailStr
    password: str

class StudentCreateResponse(BaseModel):
    id: int

    model_config = {
        "from_attributes": True
    }

# --- GET students ---
class StudentItem(BaseModel):
    id: int
    email: EmailStr

class StudentByInstitution(BaseModel):
    total: int = Field(description="Total amount of entries returned to this institution")
    limit: int = Field(description="Amount of entries to be returned")
    page: int = Field(description="Determines the offset of the query. Determined by the limit: limit*(page-1).")
    students: list[StudentItem]

# --- POST professors ---
class ProfessorCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    is_coordinator: bool = Field(description="Determines if the professor is a coordinator (Has some especial permissions)")
    coordinator_id: int | None = Field(None, description="The id of the coordinator responsible for this professor")

class ProfessorCreateResponse(BaseModel):
    id: int

# --- GET professors ---
class ProfessorItem(BaseModel):
    id: int
    name: str
    rating: float | None
    email: EmailStr
    profile_picture: str | None
    is_coordinator: int

class ProfessorByInstitution(BaseModel):
    total: int = Field(description="Total amount of entries returned to this institution")
    limit: int = Field(description="Amount of entries to be returned")
    page: int = Field(description="Determines the offset of the query. Determined by the limit: limit*(page-1).")
    professors: list[ProfessorItem]