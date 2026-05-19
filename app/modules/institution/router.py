from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.core.access_validation import validate_access_token, validate_professor
from .institution import service as institution_service
from .institution import schemas as institution_schemas
from .student.router import router as student_router
from .professor.router import router as professor_router

router = APIRouter(prefix="/institution", tags=["Instituição"])

@router.get("", response_model=institution_schemas.InstitutionObtain, status_code=200)
async def obtain_institutions(db=Depends(get_db)):
    institutions = institution_service.obtain_institution(db)
    return {"institutions": institutions}

@router.post("", response_model=institution_schemas.InstitutionCreateResponse, dependencies=[Depends(validate_professor), Depends(validate_access_token)], status_code=201)
async def create_institution(institution_in: institution_schemas.InstitutionCreate, db=Depends(get_db)):
    return institution_service.create_new_institution(institution_in, db)

router.include_router(student_router)
router.include_router(professor_router)