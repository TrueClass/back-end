from fastapi import HTTPException

_ACCESS_COLUMNS = """
    c.id AS class_id, c.professor_id, u.institution_id,
    EXISTS(SELECT 1 FROM TC.student_class sc WHERE sc.class_id = c.id AND sc.student_id = %s) AS is_enrolled,
    EXISTS(SELECT 1 FROM TC.coordinator_professor cp WHERE cp.professor_id = c.professor_id AND cp.coordinator_id = %s) AS is_supervisor
"""

CLASS_ACCESS_QUERY = f"""
    SELECT {_ACCESS_COLUMNS}
    FROM TC.class c JOIN TC.users u ON u.id = c.professor_id
    WHERE c.id = %s
"""

CLASS_ITEM_ACCESS_QUERY = f"""
    SELECT ci.id, ci.created_at, {_ACCESS_COLUMNS}
    FROM TC.class_item ci
    JOIN TC.class c ON c.id = ci.class_id
    JOIN TC.users u ON u.id = c.professor_id
    WHERE ci.id = %s
"""

def _check_access(row: dict | None, payload: dict, not_found_detail: str) -> dict:
    if not row or row["institution_id"] != payload.get("inst"):
        raise HTTPException(status_code=404, detail=not_found_detail)

    user_id = int(payload["sub"])
    if payload.get("role") == "student":
        allowed = bool(row["is_enrolled"])
    else:
        allowed = row["professor_id"] == user_id or bool(row["is_supervisor"])

    if not allowed:
        raise HTTPException(status_code=403, detail="Usuário não tem acesso a esta turma")
    return row

def _fetch(query: str, resource_id: int, payload: dict, db) -> dict | None:
    user_id = int(payload["sub"])
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(query, (user_id, user_id, resource_id))
        return cursor.fetchone()
    finally:
        cursor.close()

def get_accessible_class(class_id: int, payload: dict, db) -> dict:
    row = _fetch(CLASS_ACCESS_QUERY, class_id, payload, db)
    return _check_access(row, payload, "Turma não encontrada")

def get_accessible_class_item(class_item_id: int, payload: dict, db) -> dict:
    row = _fetch(CLASS_ITEM_ACCESS_QUERY, class_item_id, payload, db)
    return _check_access(row, payload, "Aula não encontrada")
