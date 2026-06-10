from . import models

def get_me(user_id: int, db):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.ME_SELECT_QUERY, (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
