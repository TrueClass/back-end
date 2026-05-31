from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date

# --- POST Class ---
class ClassItemInput(BaseModel):
    date: date
    title: str = Field(max_length=100)

class ClassCreate(BaseModel):
    subject: str = Field(max_length=70)
    items: list[ClassItemInput]

class ClassCreateResponse(BaseModel):
    id: int
    subject: str
    model_config = {"from_attributes": True}

# --- GET Classes ---
class ClassListItem(BaseModel):
    id: int
    subject: str
    professor_name: str | None = None

class ClassListResponse(BaseModel):
    classes: list[ClassListItem]

# --- GET Class Items ---
class ClassDateItem(BaseModel):
    created_at: str
    title: str

class ClassDatesResponse(BaseModel):
    dates: list[ClassDateItem]
