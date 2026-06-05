from pydantic import BaseModel, Field
from datetime import datetime

class RatingCreate(BaseModel):
    value: int = Field(..., ge=1, le=5)
    content: str = Field(..., max_length=280)

class RatingCreateResponse(BaseModel):
    id: int

class RatingItem(BaseModel):
    id: int
    content: str
    value: int
    boosts: int
    created_at: datetime

class RatingsByClassItem(BaseModel):
    total: int = Field(description="Total amount of ratings for this class item")
    limit: int = Field(description="Amount of entries to be returned")
    page: int = Field(description="Determines the offset of the query. Determined by the limit: limit*(page-1).")
    ratings: list[RatingItem]

class BoostResponse(BaseModel):
    boosts: int
