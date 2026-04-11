from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from . import service, schemas

# Criando uma instância do APIRouter, prefix diz que a todas as rotas começam com students e tags 
router = APIRouter(prefix="/institution", tags=["Instituição"])

@router.post("/", response_model=schemas.InstitutionCreateResponse, status_code=201)
async def create_institution(institution_in: schemas.InstitutionCreate, db = Depends(get_db)):
    new_institution = service.create_new_institution(institution_in.name,db)
    return new_institution
        
@router.get("/", response_model=schemas.InstitutionObtain, status_code=200)
async def obtain_institutions(db = Depends(get_db)):
    institutions = service.obtain_institution(db)
    return { 'institutions' : institutions }

@router.post("/{institution_id}/student", response_model=schemas.StudentCreateResponse, status_code=201)
async def create_student(institution_id: int, student_in: schemas.StudentCreate, db = Depends(get_db)):
    try:
        new_student = service.create_new_student(institution_id, student_in, db)
        return new_student
    except service.UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Este e-mail já está cadastrado.")
    
@router.get("/{institution_id}/student", response_model=schemas.StudentByInstitution, status_code=200)
async def student_by_institution(institution_id: int, limit: int, page: int,db = Depends(get_db)):
    result = service.get_student_by_institution(institution_id, limit, page, db)
    return { 'total': result[1], 'limit' : limit, 'page': page, 'students': result[0]}