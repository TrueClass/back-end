import mysql.connector
from mysql.connector import errorcode
from app.core.class_access import get_accessible_class_item
from . import models
from datetime import date

def submit_rating(class_item_id: int, payload: dict, data: object, db):
    user_id = int(payload["sub"])
    class_item = get_accessible_class_item(class_item_id, payload, db)

    if class_item["created_at"] > date.today():
        raise ClassItemIsNotValid()

    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.CHECK_ALREADY_RATED, (user_id, class_item_id))
        if cursor.fetchone():
            raise AlreadyRatedError()

        cursor.execute(models.RATING_INSERT, (user_id, class_item_id, data.content, data.value))
        rating_id = cursor.lastrowid

        professor_id = class_item["professor_id"]
        cursor.execute(models.UPDATE_PROFESSOR_RATING, (professor_id, professor_id))
        db.commit()

        return {"id": rating_id}
    except mysql.connector.IntegrityError as err:
        db.rollback()
        if err.errno == errorcode.ER_DUP_ENTRY:
            raise AlreadyRatedError()
        raise
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()

def get_ratings_by_class_item(payload: dict, class_item_id: int, limit: int, page: int, db):
    get_accessible_class_item(class_item_id, payload, db)
    user_id = int(payload["sub"])

    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.RATINGS_COUNT, (class_item_id,))
        total = cursor.fetchone()["count"]

        cursor.execute(models.USER_RATING_BY_CLASS_ITEM, (user_id, class_item_id, user_id))
        user_rating = cursor.fetchone()

        cursor.execute(models.RATINGS_BY_CLASS_ITEM, (user_id, class_item_id, user_id, limit, limit * (page - 1)))
        ratings = cursor.fetchall()

        return {"total": total, "limit": limit, "page": page, "user_rating": user_rating, "ratings": ratings}
    finally:
        cursor.close()

def _get_rating_class_item(feedback_id: int, db) -> int:
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.RATING_CLASS_ITEM, (feedback_id,))
        row = cursor.fetchone()
    finally:
        cursor.close()

    if not row:
        raise RatingNotFoundError()
    return row["class_item_id"]

def add_boost(feedback_id: int, payload: dict, db):
    user_id = int(payload["sub"])
    class_item_id = _get_rating_class_item(feedback_id, db)
    get_accessible_class_item(class_item_id, payload, db)

    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.CHECK_BOOST_EXISTS, (user_id, feedback_id))
        if cursor.fetchone():
            raise AlreadyBoostedError()

        cursor.execute(models.INSERT_BOOST, (user_id, feedback_id))
        cursor.execute(models.INCREMENT_BOOSTS, (feedback_id,))
        db.commit()

        cursor.execute(models.GET_BOOST_COUNT, (feedback_id,))
        return {"boosts": cursor.fetchone()["boosts"]}
    except mysql.connector.IntegrityError as err:
        db.rollback()
        if err.errno == errorcode.ER_DUP_ENTRY:
            raise AlreadyBoostedError()
        raise
    except Exception:
        db.rollback()
        raise
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
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()

class ClassItemIsNotValid(Exception):
    """raised when class_item date is not available for feedbacks"""
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
