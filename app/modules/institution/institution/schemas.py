from pydantic import BaseModel

class InstitutionCreate(BaseModel):
    name: str
    emails: list[str]

class InstitutionCreateResponse(BaseModel):
    id: int

    model_config = {
        "from_attributes": True
    }

class InstitutionItem(BaseModel):
    id: int
    name: str
    emails: list[str]

class InstitutionObtain(BaseModel):
    institutions: list[InstitutionItem]
