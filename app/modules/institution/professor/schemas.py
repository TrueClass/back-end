from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from datetime import date, datetime

class ProfessorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    is_coordinator: bool = Field(description="Determines if the professor is a coordinator (Has some especial permissions). Only the admin can create coordinators.")
    coordinator_id: int | None = Field(None, description="The id of the coordinator responsible for this professor. Ignored when a coordinator creates the professor (they become the coordinator).")

class ProfessorCreateResponse(BaseModel):
    id: int

class ProfessorItem(BaseModel):
    id: int
    name: str
    rating: float | None
    email: EmailStr
    profile_picture: str | None
    is_coordinator: bool

class ProfessorByInstitution(BaseModel):
    total: int = Field(description="Total amount of entries returned to this institution")
    limit: int = Field(description="Amount of entries to be returned")
    page: int = Field(description="Determines the offset of the query. Determined by the limit: limit*(page-1).")
    professors: list[ProfessorItem]

class ProfessorList(BaseModel):
    professors: list[ProfessorItem]

class ProfessorClassItem(BaseModel):
    id: int
    class_: str = Field(alias='class')
    subject: str
    last_class: date | None = None
    next_class: date | None = None
    avg_rating: float | None = None
    rating_count: int

class ProfessorClasses(BaseModel):
    professor: ProfessorItem
    classes: list[ProfessorClassItem]

class ProfessorFeedbackItem(BaseModel):
    id: int
    value: int
    content: str
    boosts: int
    created_at: datetime
    subject: str
    title: str | None = None

class ProfessorFeedbacks(BaseModel):
    most_boosted: list[ProfessorFeedbackItem]
    highest_rating: list[ProfessorFeedbackItem]
    lowest_rating: list[ProfessorFeedbackItem]

class ThemeEvidence(BaseModel):
    rating_id: int
    content: str = Field(description="Full feedback the excerpt belongs to")
    start: int = Field(description="Excerpt start inside `content`, in Unicode code points")
    end: int = Field(description="Excerpt end (exclusive) inside `content`, in Unicode code points")
    sentiment: Literal["positivo", "negativo", "neutro"]
    boosts: int
    subject: str
    title: str | None = None

class ProfessorTheme(BaseModel):
    name: str
    mentions: int = Field(description="Amount of distinct ratings that mention this theme")
    positive_share: float | None = Field(description="Share of positive opinions weighted by boosts; null when all opinions are neutral")
    evidences: list[ThemeEvidence]

class ProfessorThemesSnapshot(BaseModel):
    themes: list[ProfessorTheme]
    isolated: list[ThemeEvidence] = Field(description="Opinions that didn't group with any other rating")
    rating_count: int = Field(description="Amount of ratings the themes were generated from")
    created_at: datetime
    up_to_date: bool = Field(description="False when new ratings arrived after the themes were generated")

class ProfessorThemesStatus(BaseModel):
    snapshot: ProfessorThemesSnapshot | None = Field(description="Last stored themes, if any")
    generating: bool = Field(description="True while the themes are being generated in background")
