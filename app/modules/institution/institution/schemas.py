from pydantic import BaseModel, BeforeValidator, Field, StringConstraints
from typing import Annotated

Domain = Annotated[
    str,
    BeforeValidator(lambda v: v.strip().lower() if isinstance(v, str) else v),
    StringConstraints(min_length=3, max_length=254, pattern=r"^[a-z0-9.-]+\.[a-z]{2,}$"),
]

class InstitutionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=45)
    emails: list[Domain] = Field(min_length=1, max_length=20, description="E-mail domains accepted by the institution, e.g. alunos.fho.edu.br")

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
