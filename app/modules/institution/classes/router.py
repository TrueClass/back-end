from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.core.access_validation import validate_access_token, validate_professor
from . import service, schemas

router = APIRouter()

@router.get("/{institution_id}/classes", response_model=schemas.ClassListResponse, status_code=200)
async def get_classes(institution_id: int, db=Depends(get_db), payload=Depends(validate_access_token)):
    user_id = payload.get("sub")
    role = payload.get("role")
    classes = service.get_classes(user_id, role, db)
    return {"classes": classes}

@router.post("/{institution_id}/classes", response_model=schemas.ClassCreateResponse, dependencies=[Depends(validate_professor)], status_code=201)
async def create_class(institution_id: int, class_in: schemas.ClassCreate, db=Depends(get_db), payload=Depends(validate_access_token)):
    user_id = payload.get("sub")
    return service.create_new_class(class_in, user_id, db)

@router.get("/{institution_id}/classes/{class_id}/items", response_model=schemas.ClassDatesResponse, status_code=200, dependencies=[Depends(validate_access_token)])
async def get_class_items(institution_id: int, class_id: int, db=Depends(get_db)):
    result = service.get_class_items(class_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="No date found for this classes")
    return {"dates": result}