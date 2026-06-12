from pydantic import BaseModel, Field
from datetime import date
from typing import Literal

# --- POST Class ---
class ClassCreate(BaseModel):
    subject: str = Field(max_length=70)
    class_name: str = Field(max_length=70)
    start_date: date
    end_date: date
    frequency: Literal["weekly", "biweekly_a", "biweekly_b"]
    titles: list[str] = Field(min_length=1)

class EnrollResponse(BaseModel):
    id: int
    linked: bool

class ClassCreateResponse(BaseModel):
    id: int
    subject: str
    model_config = {"from_attributes": True}

# --- GET Classes ---
class ClassListItem(BaseModel):
    id: int
    class_: str = Field(alias='class')
    subject: str
    professor_name: str | None = None

class ClassListResponse(BaseModel):
    classes: list[ClassListItem]

# --- GET Class Items ---
class ClassDateItem(BaseModel):
    id: int
    created_at: date
    title: str

class ClassDatesResponse(BaseModel):
    dates: list[ClassDateItem]

