from pydantic import BaseModel, EmailStr

class MeResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    institution_id: int
    institution_name: str
    name: str | None = None
    rating: float | None = None
    profile_picture: str | None = None
    is_coordinator: bool | None = None
