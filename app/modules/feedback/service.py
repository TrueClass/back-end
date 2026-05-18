from app.modules.login.service import fetch_user_info
from . import models

def submit_rating(class_item_id: int, student_email: str, data: object, db):
    cursor = db.cursor(dictionary=True)

    try:
        student = fetch_user_info(student_email, db)
        student_id = student["id"]

        cursor.execute(models.CHECK_CLASS_ITEM_EXISTS, (class_item_id,))
        class_item = cursor.fetchone()
        if not class_item:
            raise ClassItemNotFoundError()

        cursor.execute(models.CHECK_STUDENT_ENROLLED, (student_id, class_item_id))
        if not cursor.fetchone():
            raise StudentNotEnrolledError()

        cursor.execute(models.CHECK_ALREADY_RATED, (student_id, class_item_id))
        if cursor.fetchone():
            raise AlreadyRatedError()

        cursor.execute(models.RATING_INSERT, (student_id, class_item_id, data.content, data.value))
        db.commit()

        return {"id": cursor.lastrowid}
    finally:
        cursor.close()

def get_ratings_by_class_item(class_item_id: int, limit: int, page: int, db):
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(models.RATINGS_COUNT, (class_item_id,))
        total = cursor.fetchone()["count"]

        cursor.execute(models.RATINGS_BY_CLASS_ITEM, (class_item_id, limit, limit * (page - 1)))
        ratings = cursor.fetchall()

        return (total, ratings)
    finally:
        cursor.close()

class ClassItemNotFoundError(Exception):
    """Raised when the class_item_id does not exist"""
    pass

class StudentNotEnrolledError(Exception):
    """Raised when the student is not enrolled in the class that contains the class_item"""
    pass

class AlreadyRatedError(Exception):
    """Raised when the student has already submitted a rating for this class_item"""
    pass
