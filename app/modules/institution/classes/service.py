from . import models
from datetime import timedelta
from fastapi import HTTPException

def link_class_student(user_id, class_id, db):
    cursor = db.cursor(dictionary=True)

    try:

        # validate if classes exist
        cursor.execute(models.VALIDATE_CLASS_ID_QUERY, (class_id,))

        existing_class = cursor.fetchone()

        if not existing_class:
            raise HTTPException(
                status_code=404,
                detail="Class not found"
            )

        # validate if student is alredy linked
        cursor.execute(models.VALIDATE_STUDENT_CLASS_LINK_QUERY, (user_id, class_id))
        existing_link = cursor.fetchone()

        if existing_link:
            raise HTTPException(
                status_code=409,
                detail="Student already linked to this classes"
            )

        # create link
        values = (user_id, class_id)
        cursor.execute(models.STUDENT_CLASS_LINK_QUERY, values)
        db.commit()

        return {
            "id": cursor.lastrowid,
            "linked": True
        }

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()

def calculate_dates(start_date, end_date, is_biweekly, biweekly_week=None) -> list:
    all_weeks = []

    # Weekly classes
    if not is_biweekly:
        current = start_date
        while current <= end_date:
            all_weeks.append(current)
            current += timedelta(days=7)
        return all_weeks

    # biweekly A
    if biweekly_week == "A":
        current = start_date
    # biweekly B
    elif biweekly_week == "B":
        current = start_date + timedelta(days=7)
    else:
        raise ValueError("biweekly_week must be 'A' or 'B'")

    while current <= end_date:
        all_weeks.append(current)
        current += timedelta(days=14)

    return all_weeks


def create_new_class(data: object, user_id: int, db) -> object:
    cursor = db.cursor(dictionary=True)
    try:
        dates = calculate_dates(
            data.start_date,
            data.end_date,
            data.is_biweekly,
            data.biweekly_week
        )
        biweekly = 1 if data.is_biweekly else 0
        values = (
            data.subject,
            biweekly,
            data.biweekly_week,
            user_id
        )
        cursor.execute(models.CLASS_INSERT_QUERY, values)
        class_id = cursor.lastrowid

        values = [(str(class_date), class_id) for class_date in dates]
        cursor.executemany(models.CLASS_ITEM_INSERT_QUERY, values)

        db.commit()
        return {"id": class_id, "subject": data.subject}
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()


def get_classes(user_id: int, role: str, db):
    cursor = db.cursor(dictionary=True)
    try:
        if role == "student":
            cursor.execute(models.CLASS_GET_BY_STUDENT_QUERY, (user_id,))
        else:
            cursor.execute(models.CLASS_GET_BY_PROFESSOR_QUERY, (user_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        cursor.close()


def get_class_items(class_id: int, db):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.CLASS_ITEMS_GET_QUERY, (class_id,))
        rows = cursor.fetchall()
        return [row["date"] for row in rows]
    finally:
        cursor.close()