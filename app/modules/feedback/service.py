from . import models
from datetime import date

def submit_rating(class_item_id: int, user_id: int, data: object, db):
    cursor = db.cursor(dictionary=True)
    current_date = date.today()

    try:
        cursor.execute(models.CHECK_CLASS_ITEM_EXISTS, (current_date, class_item_id))
        class_item = cursor.fetchone()

        if not class_item.get("is_valid"):
            raise ClassItemIsNotValid()

        if not class_item:
            raise ClassItemNotFoundError()

        cursor.execute(models.CHECK_STUDENT_ENROLLED, (user_id, class_item_id))
        if not cursor.fetchone():
            raise StudentNotEnrolledError()

        cursor.execute(models.CHECK_ALREADY_RATED, (user_id, class_item_id))
        if cursor.fetchone():
            raise AlreadyRatedError()

        cursor.execute(models.RATING_INSERT, (user_id, class_item_id, data.content, data.value))
        db.commit()

        return {"id": cursor.lastrowid}
    finally:
        cursor.close()

def get_ratings_by_class_item(payload, class_item_id: int, limit: int, page: int, db):
    cursor = db.cursor(dictionary=True)
    student_id = payload.get("sub")

    try:
        cursor.execute(models.RATINGS_COUNT, (class_item_id,))
        total = cursor.fetchone()["count"]

        cursor.execute(models.RATINGS_BY_CLASS_ITEM, (student_id, student_id, class_item_id, limit, limit * (page - 1)))
        ratings = cursor.fetchall()

        return (total, ratings)
    finally:
        cursor.close()

def add_boost(feedback_id: int, user_id: int, db):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.CHECK_RATING_EXISTS, (feedback_id,))
        if not cursor.fetchone():
            raise RatingNotFoundError()

        cursor.execute(models.CHECK_BOOST_EXISTS, (user_id, feedback_id))
        if cursor.fetchone():
            raise AlreadyBoostedError()

        cursor.execute(models.INSERT_BOOST, (user_id, feedback_id))
        cursor.execute(models.INCREMENT_BOOSTS, (feedback_id,))
        db.commit()

        cursor.execute(models.GET_BOOST_COUNT, (feedback_id,))
        return {"boosts": cursor.fetchone()["boosts"]}
    finally:
        cursor.close()

def remove_boost(feedback_id: int, user_id: int, db):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.CHECK_BOOST_EXISTS, (user_id, feedback_id))
        if not cursor.fetchone():
            raise BoostNotFoundError()

        cursor.execute(models.DELETE_BOOST, (user_id, feedback_id))
        cursor.execute(models.DECREMENT_BOOSTS, (feedback_id,))
        db.commit()

        cursor.execute(models.GET_BOOST_COUNT, (feedback_id,))
        return {"boosts": cursor.fetchone()["boosts"]}
    finally:
        cursor.close()

class ClassItemIsNotValid(Exception):
    """raised when class_item date is not available for feedbacks"""

class ClassItemNotFoundError(Exception):
    """Raised when the class_item_id does not exist"""
    pass

class StudentNotEnrolledError(Exception):
    """Raised when the student is not enrolled in the classes that contains the class_item"""
    pass

class AlreadyRatedError(Exception):
    """Raised when the student has already submitted a rating for this class_item"""
    pass

class RatingNotFoundError(Exception):
    """Raised when the rating_id does not exist or is inactive"""
    pass

class AlreadyBoostedError(Exception):
    """Raised when the user has already boosted this rating"""
    pass

class BoostNotFoundError(Exception):
    """Raised when the user has not boosted this rating"""
    pass
