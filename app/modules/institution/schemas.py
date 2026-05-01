from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date

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

# --- POST Class ---
class ClassCreate(BaseModel):
    subject: str = Field(max_length=70)
    is_biweekly: bool
    biweekly_week: str | None = None
    start_date: date
    end_date: date

    @field_validator("biweekly_week")
    def validate_isbeweekly_week(cls, v, info):
        is_beweekly = info.data.get("is_biweekly")
        if is_beweekly:
            if v not in ("A", "B"):
                raise ValueError("biweekly_week must be 'A' or 'B'")
        else:
            if v is not None:
                raise ValueError("biweekly_week must be None when biweekly=False")
        return v

    @field_validator("end_date")
    def validate_end_date(cls, v, info):
        start_date = info.data.get("start_date")
        if start_date and v <= start_date:
            raise ValueError("end_date must be greater than start_date")
        return v


class ClassCreateResponse(BaseModel):
    id: int
    subject: str
    model_config = {"from_attributes": True}


# --- GET Class ---
class ClassListItem(BaseModel):
    id: int
    subject: str
    professor_name: str | None = None
    biweekly: bool
    biweekly_week: str | None = None


class ClassListResponse(BaseModel):
    classes: list[ClassListItem]


class ClassDatesResponse(BaseModel):
    dates: list[str]