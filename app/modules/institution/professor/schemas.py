from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime

class ProfessorCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    is_coordinator: bool = Field(description="Determines if the professor is a coordinator (Has some especial permissions)")
    coordinator_id: int | None = Field(None, description="The id of the coordinator responsible for this professor")

class ProfessorCreateResponse(BaseModel):
    id: int

class ProfessorItem(BaseModel):
    id: int
    name: str
    rating: float | None
    email: EmailStr
    profile_picture: str | None
    is_coordinator: bool

class ProfessorList(BaseModel):
    total: int = Field(description="Total amount of entries returned to this institution")
    limit: int = Field(description="Amount of entries to be returned")
    page: int = Field(description="Determines the offset of the query. Determined by the limit: limit*(page-1).")
    professors: list[ProfessorItem]

class ProfessorClassItem(BaseModel):
    id: int
    class_: str = Field(alias='class')
    subject: str
    last_class: date | None = None
    next_class: date | None = None
    model_config = {"populate_by_name": True}

class ProfessorClassesResponse(BaseModel):
    classes: list[ProfessorClassItem]

class FeedbackItem(BaseModel):
    id: int
    content: str
    value: int
    boosts: int
    created_at: datetime

class ProfessorFeedbacksResponse(BaseModel):
    most_boosted: list[FeedbackItem]
    highest_rating: list[FeedbackItem]
    lowest_rating: list[FeedbackItem]