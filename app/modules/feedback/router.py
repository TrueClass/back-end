from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.database import get_db
from app.core.access_validation import validate_access_token, validate_student
from . import service, schemas

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post("/{class_item_id}", response_model=schemas.RatingCreateResponse, status_code=201)
async def submit_rating(
    class_item_id: int,
    rating_in: schemas.RatingCreate,
    token_data: dict = Depends(validate_access_token),
    _: None = Depends(validate_student),
    db=Depends(get_db)
):
    try:
        result = service.submit_rating(class_item_id, int(token_data["sub"]), rating_in, db)
        return result
    except service.ClassItemIsNotValid:
        raise HTTPException(status_code=422, detail="Class item date not available for feedbacks")
    except service.ClassItemNotFoundError:
        raise HTTPException(status_code=404, detail="Class item not found")
    except service.StudentNotEnrolledError:
        raise HTTPException(status_code=403, detail="Student is not enrolled in this classes")
    except service.AlreadyRatedError:
        raise HTTPException(status_code=409, detail="Student has already rated this classes item")
    except service.InappropriateContentError as e:
        raise HTTPException(status_code=400, detail=f"Blocked: {e.reason}")

@router.get("/{class_item_id}", response_model=schemas.RatingsByClassItem, dependencies=[Depends(validate_access_token)], status_code=200)
async def get_ratings(
    class_item_id: int,
    limit: int = Query(10, ge=1),
    page: int = Query(1, ge=1),
    db=Depends(get_db),
    payload=Depends(validate_access_token)
):
    
    result = service.get_ratings_by_class_item(payload, class_item_id, limit, page, db)
    return {"total": result[0], "limit": limit, "page": page, "ratings": result[1]}

@router.post("/{feedback_id}/boost", response_model=schemas.BoostResponse, status_code=201)
async def add_boost(
    feedback_id: int,
    token_data: dict = Depends(validate_access_token),
    db=Depends(get_db)
):
    try:
        return service.add_boost(feedback_id, int(token_data["sub"]), db)
    except service.RatingNotFoundError:
        raise HTTPException(status_code=404, detail="Feedback item not found")
    except service.AlreadyBoostedError:
        raise HTTPException(status_code=409, detail="User already boosted this item")

@router.delete("/{feedback_id}/boost", response_model=schemas.BoostResponse, status_code=200)
async def remove_boost(
    feedback_id: int,
    token_data: dict = Depends(validate_access_token),
    db=Depends(get_db)
):
    try:
        return service.remove_boost(feedback_id, int(token_data["sub"]), db)
    except service.BoostNotFoundError:
        raise HTTPException(status_code=404, detail="User has not boosted this item")
