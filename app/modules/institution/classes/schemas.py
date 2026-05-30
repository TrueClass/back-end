from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date

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