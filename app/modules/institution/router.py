from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.core.access_validation import validate_access_token, validate_professor
from . import service, schemas

# Criando uma instância do APIRouter, prefix diz que a todas as rotas começam com students e tags 
router = APIRouter(prefix="/institution", tags=["Instituição"])

@router.get("/", response_model=schemas.InstitutionObtain, status_code=200)
async def obtain_institutions(db = Depends(get_db)):
    institutions = service.obtain_institution(db)
    return { 'institutions' : institutions }

@router.post("/", response_model=schemas.InstitutionCreateResponse, dependencies=[Depends(validate_professor), Depends(validate_access_token)], status_code=201)
async def create_institution(institution_in: schemas.InstitutionCreate, db = Depends(get_db)):
    new_institution = service.create_new_institution(institution_in, db)
    return new_institution        
    
@router.get("/{institution_id}/student", response_model=schemas.StudentByInstitution, dependencies=[Depends(validate_access_token)], status_code=200)
async def student_by_institution(institution_id: int, limit: int, page: int, db = Depends(get_db)):
    result = service.get_student_by_institution(institution_id, limit, page, db)
    return { 'total': result[0], 'limit' : limit, 'page': page, 'students': result[1]}

@router.post("/{institution_id}/student", response_model=schemas.StudentCreateResponse, dependencies=[Depends(validate_professor), Depends(validate_access_token)], status_code=201)
async def create_student(institution_id: int, student_in: schemas.StudentCreate, db = Depends(get_db)):
    try:
        new_student = service.create_new_student(institution_id, student_in, db)
        return new_student
    except service.UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="This e-mail already exists.")
    except service.InstitutionDoesntExistError:
        raise HTTPException(status_code=422, detail="Institution informed doesn't exist")

@router.get("/{institution_id}/professor", response_model=schemas.ProfessorByInstitution, dependencies=[Depends(validate_access_token)], status_code=200)
async def professor_by_institution(institution_id: int, limit: int, page: int,db = Depends(get_db)):
    result = service.get_professor_by_institution(institution_id, limit, page, db)
    return { 'total': result[0], 'limit' : limit, 'page': page, 'professors': result[1]}

@router.post("/{institution_id}/professor", response_model=schemas.ProfessorCreateResponse, dependencies=[Depends(validate_professor), Depends(validate_access_token)], status_code=201)
async def create_professor(institution_id: int, professor_in: schemas.ProfessorCreate, db = Depends(get_db)):
    try:
        new_professor = service.create_new_professor(institution_id, professor_in, db)
        return new_professor
    except service.UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="This e-mail already exists.")
    except service.InstitutionDoesntExistError:
        raise HTTPException(status_code=422, detail="Institution informed doesn't exist")
    except service.CoordinatorDoesntExistError:
        raise HTTPException(status_code=422, detail="Coordinator informed doesn't exist")