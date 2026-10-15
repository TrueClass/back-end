from pydantic import BaseModel, Field, StringConstraints, model_validator
from datetime import date, timedelta
from typing import Annotated, Literal

MAX_PERIOD_DAYS = 186
MAX_CLASS_ITEMS = 30

Title = Annotated[str, StringConstraints(strip_whitespace=True, max_length=280)]

# --- POST Class ---
class ClassCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=70)
    class_name: str = Field(min_length=1, max_length=70)
    start_date: date
    end_date: date
    frequency: Literal["weekly", "biweekly_a", "biweekly_b"]
    titles: list[Title] = Field(min_length=1, max_length=MAX_CLASS_ITEMS)

    @model_validator(mode="after")
    def check_period(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date deve ser igual ou posterior a start_date")
        if self.end_date > self.start_date + timedelta(days=MAX_PERIOD_DAYS):
            raise ValueError(f"O período não pode exceder {MAX_PERIOD_DAYS} dias")
        return self

class ClassCreateResponse(BaseModel):
    id: int
    subject: str
    join_code: str

class EnrollRequest(BaseModel):
    code: str = Field(min_length=1, max_length=10)

class EnrollResponse(BaseModel):
    id: int
    class_id: int
    linked: bool

# --- GET Classes ---
class Class(BaseModel):
    id: int
    class_: str = Field(alias='class')
    subject: str
    professor_name: str | None = None
    join_code: str | None = Field(None, description="Only returned to the professor who owns the class")
    last_class: date | None = None
    next_class: date | None = None

class ClassResponse(BaseModel):
    classes: list[Class]

# --- GET Class Items ---
class ClassDateItem(BaseModel):
    id: int
    created_at: date
    title: str | None = None
    avg_rating: float | None = None
    rating_count: int
    rated_by_user: bool = False

class ClassDatesResponse(BaseModel):
    info: Class
    dates: list[ClassDateItem]
