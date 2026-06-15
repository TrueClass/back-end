from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.database import get_db
from app.core.access_validation import validate_coordinator, validate_professor, validate_access_token
from ..exceptions import UserAlreadyExistsError, InstitutionDoesntExistError, CoordinatorDoesntExistError
from . import service, schemas

router = APIRouter()

@router.get("/{institution_id}/professor_by_institution", response_model=schemas.ProfessorList, dependencies=[Depends(validate_professor)], status_code=200)
async def professor_by_institution(institution_id: int, limit: int = Query(10, ge=1), page: int = Query(1, ge=1), db=Depends(get_db)):
    total, professors = service.get_professor_by_institution(institution_id, limit, page, db)
    return {"total": total, "limit": limit, "page": page, "professors": professors}

@router.get("/{institution_id}/professor_by_coordinator", response_model=schemas.ProfessorList, dependencies=[Depends(validate_professor)], status_code=200)
async def professor_by_coordinator(institution_id: int, limit: int = Query(10, ge=1), page: int = Query(1, ge=1), db=Depends(get_db), payload=Depends(validate_access_token)):
    total, professors = service.get_professor_by_coordinator(institution_id, payload, limit, page, db)
    return {"total": total, "limit": limit, "page": page, "professors": professors}

@router.post("/{institution_id}/professor", response_model=schemas.ProfessorCreateResponse, dependencies=[Depends(validate_coordinator)], status_code=201)
async def create_professor(institution_id: int, professor_in: schemas.ProfessorCreate, db=Depends(get_db)):
    try:
        return service.create_new_professor(institution_id, professor_in, db)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="This e-mail already exists.")
    except InstitutionDoesntExistError:
        raise HTTPException(status_code=422, detail="Institution informed doesn't exist")
    except CoordinatorDoesntExistError:
        raise HTTPException(status_code=422, detail="Coordinator informed doesn't exist")