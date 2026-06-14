from . import models
from fastapi import HTTPException
from datetime import date, timedelta

def calculate_class_dates(start_date: date, end_date: date, frequency: str) -> list[date]:
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    dates = []

    if frequency == "weekly":
        current = start_date
        while current <= end_date:
            dates.append(current)
            current += timedelta(weeks=1)

    elif frequency == "biweekly_a":
        current = start_date
        while current <= end_date:
            dates.append(current)
            current += timedelta(weeks=2)

    elif frequency == "biweekly_b":
        current = start_date + timedelta(weeks=1)
        while current <= end_date:
            dates.append(current)
            current += timedelta(weeks=2)

    else:
        raise HTTPException(status_code=400, detail="Invalid frequency")

    return dates

def link_class_student(user_id, class_id, db):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.VALIDATE_CLASS_ID_QUERY, (class_id,))
        existing_class = cursor.fetchone()
        if not existing_class:
            raise HTTPException(status_code=404, detail="Class not found")

        cursor.execute(models.VALIDATE_STUDENT_CLASS_LINK_QUERY, (user_id, class_id))
        existing_link = cursor.fetchone()
        if existing_link:
            raise HTTPException(status_code=409, detail="Student already linked to this class")

        cursor.execute(models.STUDENT_CLASS_LINK_QUERY, (user_id, class_id))
        db.commit()
        return {"id": cursor.lastrowid, "linked": True}
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()


def create_new_class(data, user_id, db):
    cursor = db.cursor(dictionary=True)
    try:
        dates = calculate_class_dates(data.start_date, data.end_date, data.frequency)

        if not dates:
            raise HTTPException(status_code=400, detail="No class dates generated for the given range and frequency")

        cursor.execute(models.CLASS_INSERT_QUERY, (data.subject, user_id, data.class_name))
        class_id = cursor.lastrowid

        titles = data.titles[:len(dates)]
        while len(titles) < len(dates):
            titles.append(f"Aula {len(titles) + 1}")

        values = [(str(d), class_id, titles[i]) for i, d in enumerate(dates)]
        cursor.executemany(models.CLASS_ITEM_INSERT_QUERY, values)

        db.commit()
        return {"id": class_id, "subject": data.subject, "class": data.class_name}
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()


def get_classes(payload, db):
    user_id = int(payload.get("sub"))
    role = payload.get("role")
    current_date = date.today()

    cursor = db.cursor(dictionary=True)
    try:
        if role == "student":
            cursor.execute(models.CLASS_GET_BY_STUDENT_QUERY, (current_date, current_date, user_id))
        elif role == "professor":
            cursor.execute(models.CLASS_GET_BY_PROFESSOR_QUERY, (current_date, current_date, user_id))
        else:
            raise HTTPException(
                status_code=403,
                detail="Invalid role"
            )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        cursor.close()


def get_class_items(class_id, db):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.CLASS_ITEMS_GET_QUERY, (class_id,))
        return [{"id": row["id"], "created_at": row["created_at"], "title": row["title"]} for row in cursor.fetchall()]
    finally:
        cursor.close()