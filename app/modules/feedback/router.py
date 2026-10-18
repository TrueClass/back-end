from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.database import get_db
from app.core.access_validation import validate_access_token, validate_student
from . import service, schemas

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post("/{class_item_id}", response_model=schemas.RatingCreateResponse, status_code=201)
async def submit_rating(
    class_item_id: int,
    rating_in: schemas.RatingCreate,
    payload: dict = Depends(validate_student),
    db=Depends(get_db)
):
    try:
        return service.submit_rating(class_item_id, payload, rating_in, db)
    except service.ClassItemIsNotValid:
        raise HTTPException(status_code=422, detail="Esta aula ainda não está disponível para avaliação")
    except service.AlreadyRatedError:
        raise HTTPException(status_code=409, detail="Você já avaliou esta aula")
    except service.InappropriateContentError as e:
        raise HTTPException(status_code=400, detail=f"Blocked: {e.reason}")

@router.get("/{class_item_id}", response_model=schemas.RatingsByClassItem, status_code=200)
async def get_ratings(
    class_item_id: int,
    limit: int = Query(10, ge=1, le=50),
    page: int = Query(1, ge=1),
    db=Depends(get_db),
    payload: dict = Depends(validate_access_token)
):
    return service.get_ratings_by_class_item(payload, class_item_id, limit, page, db)

@router.post("/{feedback_id}/boost", response_model=schemas.BoostResponse, status_code=201)
async def add_boost(
    feedback_id: int,
    payload: dict = Depends(validate_student),
    db=Depends(get_db)
):
    try:
        return service.add_boost(feedback_id, payload, db)
    except service.RatingNotFoundError:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    except service.AlreadyBoostedError:
        raise HTTPException(status_code=409, detail="Você já deu boost nesta avaliação")

@router.delete("/{feedback_id}/boost", response_model=schemas.BoostResponse, status_code=200)
async def remove_boost(
    feedback_id: int,
    payload: dict = Depends(validate_student),
    db=Depends(get_db)
):
    try:
        return service.remove_boost(feedback_id, int(payload["sub"]), db)
    except service.BoostNotFoundError:
        raise HTTPException(status_code=404, detail="Você não deu boost nesta avaliação")
