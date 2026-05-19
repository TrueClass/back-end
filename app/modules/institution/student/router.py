from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.database import get_db
from app.core.access_validation import validate_access_token, validate_professor
from ..exceptions import UserAlreadyExistsError, InstitutionDoesntExistError
from . import service, schemas

router = APIRouter()

@router.get("/{institution_id}/student", response_model=schemas.StudentByInstitution, dependencies=[Depends(validate_access_token)], status_code=200)
async def student_by_institution(institution_id: int, limit: int = Query(10, ge=1), page: int = Query(1, ge=1), db=Depends(get_db)):
    total, students = service.get_student_by_institution(institution_id, limit, page, db)
    return {"total": total, "limit": limit, "page": page, "students": students}

@router.post("/{institution_id}/student", response_model=schemas.StudentCreateResponse, dependencies=[Depends(validate_professor), Depends(validate_access_token)], status_code=201)
async def create_student(institution_id: int, student_in: schemas.StudentCreate, db=Depends(get_db)):
    try:
        return service.create_new_student(institution_id, student_in, db)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="This e-mail already exists.")
    except InstitutionDoesntExistError:
        raise HTTPException(status_code=422, detail="Institution informed doesn't exist")
