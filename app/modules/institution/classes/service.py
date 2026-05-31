from . import models
from fastapi import HTTPException

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
        cursor.execute(models.CLASS_INSERT_QUERY, (data.subject, user_id))
        class_id = cursor.lastrowid

        values = [(str(item.date), class_id, item.title) for item in data.items]
        cursor.executemany(models.CLASS_ITEM_INSERT_QUERY, values)

        db.commit()
        return {"id": class_id, "subject": data.subject}
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()


def get_classes(user_id, role, db):
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


def get_class_items(class_id, db):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.CLASS_ITEMS_GET_QUERY, (class_id,))
        rows = cursor.fetchall()
        return [{"created_at": str(row["created_at"]), "title": row["title"]} for row in rows]
    finally:
        cursor.close()