from fastapi import APIRouter, Depends, HTTPException
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
        result = service.submit_rating(class_item_id, token_data["sub"], rating_in, db)
        return result
    except service.ClassItemNotFoundError:
        raise HTTPException(status_code=404, detail="Class item not found")
    except service.StudentNotEnrolledError:
        raise HTTPException(status_code=403, detail="Student is not enrolled in this class")
    except service.AlreadyRatedError:
        raise HTTPException(status_code=409, detail="Student has already rated this class item")

@router.get("/{class_item_id}", response_model=schemas.RatingsByClassItem, dependencies=[Depends(validate_access_token)], status_code=200)
async def get_ratings(
    class_item_id: int,
    limit: int,
    page: int,
    db=Depends(get_db)
):
    result = service.get_ratings_by_class_item(class_item_id, limit, page, db)
    return {"total": result[0], "limit": limit, "page": page, "ratings": result[1]}
