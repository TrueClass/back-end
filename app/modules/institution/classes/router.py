from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.core.access_validation import validate_institution_member, validate_professor, validate_student
from . import service, schemas

router = APIRouter()

@router.get("/{institution_id}/classes", response_model=schemas.ClassResponse, status_code=200)
async def get_classes(institution_id: int, db=Depends(get_db), payload=Depends(validate_institution_member)):
    return {"classes": service.get_classes(payload, db)}

@router.post("/{institution_id}/classes", response_model=schemas.ClassCreateResponse, dependencies=[Depends(validate_professor)], status_code=201)
async def create_class(institution_id: int, class_in: schemas.ClassCreate, db=Depends(get_db), payload=Depends(validate_institution_member)):
    return service.create_new_class(class_in, int(payload["sub"]), institution_id, db)

@router.post("/{institution_id}/classes/enroll", response_model=schemas.EnrollResponse, dependencies=[Depends(validate_student)], status_code=201)
async def enroll_class(institution_id: int, enroll_in: schemas.EnrollRequest, db=Depends(get_db), payload=Depends(validate_institution_member)):
    return service.link_class_student(int(payload["sub"]), institution_id, enroll_in.code, db)

@router.get("/{institution_id}/classes/{class_id}/items", response_model=schemas.ClassDatesResponse, status_code=200)
async def get_class_items(institution_id: int, class_id: int, db=Depends(get_db), payload=Depends(validate_institution_member)):
    return service.get_class_items(class_id, payload, db)
