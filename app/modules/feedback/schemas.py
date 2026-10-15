from pydantic import BaseModel, Field
from datetime import datetime

class RatingCreate(BaseModel):
    value: int = Field(..., ge=1, le=5)
    content: str = Field(..., min_length=1, max_length=280)

class RatingCreateResponse(BaseModel):
    id: int

class RatingItem(BaseModel):
    id: int
    content: str
    value: int
    boosts: int
    created_at: datetime
    sent_by_user: bool
    boosted_by_user: bool

class RatingsByClassItem(BaseModel):
    total: int = Field(description="Total amount of ratings for this classes item, including the user's own")
    limit: int = Field(description="Amount of entries to be returned")
    page: int = Field(description="Determines the offset of the query. Determined by the limit: limit*(page-1).")
    user_rating: RatingItem | None = Field(None, description="Rating sent by the requesting user, if any. Never repeated inside `ratings`.")
    ratings: list[RatingItem]

class BoostResponse(BaseModel):
    boosts: int
