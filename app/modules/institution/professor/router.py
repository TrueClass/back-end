from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Query
from typing import Annotated
from app.core.database import get_db
from app.core.access_validation import (
    validate_access_token, validate_professor, validate_coordinator,
    validate_institution_member, is_admin_key_valid
)
from ..exceptions import UserAlreadyExistsError, InstitutionDoesntExistError, CoordinatorDoesntExistError
from . import service, schemas

router = APIRouter()

async def get_professor_creator(
    institution_id: int,
    x_admin_key: Annotated[str | None, Header()] = None,
    access_token: Annotated[str | None, Cookie()] = None
) -> dict | None:
    if is_admin_key_valid(x_admin_key):
        return None
    payload = await validate_access_token(access_token)
    if payload.get("role") != "professor" or not payload.get("coord") or payload.get("inst") != institution_id:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")
    return payload

@router.get("/{institution_id}/professor", response_model=schemas.ProfessorByInstitution, dependencies=[Depends(validate_institution_member)], status_code=200)
async def professor_by_institution(institution_id: int, limit: int = Query(10, ge=1, le=100), page: int = Query(1, ge=1), db=Depends(get_db)):
    total, professors = service.get_professor_by_institution(institution_id, limit, page, db)
    return {"total": total, "limit": limit, "page": page, "professors": professors}

@router.post("/{institution_id}/professor", response_model=schemas.ProfessorCreateResponse, status_code=201)
async def create_professor(institution_id: int, professor_in: schemas.ProfessorCreate, creator: dict | None = Depends(get_professor_creator), db=Depends(get_db)):
    if creator is None:
        coordinator_id = professor_in.coordinator_id
    else:
        if professor_in.is_coordinator:
            raise HTTPException(status_code=403, detail="Apenas o administrador pode criar coordenadores")
        coordinator_id = int(creator["sub"])

    try:
        return service.create_new_professor(institution_id, professor_in, coordinator_id, db)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Este e-mail já está cadastrado.")
    except InstitutionDoesntExistError:
        raise HTTPException(status_code=422, detail="A instituição informada não existe")
    except CoordinatorDoesntExistError:
        raise HTTPException(status_code=422, detail="O coordenador informado não existe nesta instituição")

@router.get("/{institution_id}/professor_by_coordinator", response_model=schemas.ProfessorList, status_code=200)
async def professors_by_coordinator(institution_id: int, payload: dict = Depends(validate_coordinator), _: dict = Depends(validate_institution_member), db=Depends(get_db)):
    return {"professors": service.get_professors_by_coordinator(int(payload["sub"]), institution_id, db)}

@router.get("/{institution_id}/professor/{professor_id}/classes", response_model=schemas.ProfessorClasses, dependencies=[Depends(validate_professor)], status_code=200)
async def professor_classes(institution_id: int, professor_id: int, payload: dict = Depends(validate_institution_member), db=Depends(get_db)):
    return service.get_professor_classes(institution_id, professor_id, payload, db)

@router.get("/{institution_id}/professor/{professor_id}/feedbacks", response_model=schemas.ProfessorFeedbacks, dependencies=[Depends(validate_professor)], status_code=200)
async def professor_feedbacks(institution_id: int, professor_id: int, limit: int = Query(5, ge=1, le=20), payload: dict = Depends(validate_institution_member), db=Depends(get_db)):
    return service.get_professor_feedbacks(institution_id, professor_id, limit, payload, db)
