# --- INSERT Queries ---
CLASS_INSERT_QUERY = "INSERT INTO TC.class (subject, professor_id, institution_id, class, join_code) VALUES (%s, %s, %s, %s, %s)"
CLASS_ITEM_INSERT_QUERY = "INSERT INTO TC.class_item (created_at, class_id, title) VALUES (%s, %s, %s)"
STUDENT_CLASS_LINK_QUERY = "INSERT INTO TC.student_class (student_id, class_id) VALUES (%s, %s)"

# --- GET Queries ---
CLASS_GET_BY_STUDENT_QUERY = """
    SELECT c.id, c.class, c.subject, p.name AS professor_name,
           MAX(CASE WHEN ci.created_at < %s THEN ci.created_at END) AS last_class,
           MIN(CASE WHEN ci.created_at >= %s THEN ci.created_at END) AS next_class
    FROM TC.class c
    JOIN TC.professor_profile p ON p.user_id = c.professor_id
    JOIN TC.student_class sc ON sc.class_id = c.id
    LEFT JOIN TC.class_item ci ON c.id = ci.class_id
    WHERE sc.student_id = %s
    GROUP BY c.id, c.class, c.subject, p.name
"""
CLASS_GET_BY_PROFESSOR_QUERY = """
    SELECT c.id, c.class, c.subject, c.join_code, p.name AS professor_name,
           MAX(CASE WHEN ci.created_at < %s THEN ci.created_at END) AS last_class,
           MIN(CASE WHEN ci.created_at >= %s THEN ci.created_at END) AS next_class
    FROM TC.class c
    JOIN TC.professor_profile p ON p.user_id = c.professor_id
    LEFT JOIN TC.class_item ci ON c.id = ci.class_id
    WHERE c.professor_id = %s
    GROUP BY c.id, c.class, c.subject, c.join_code, p.name
"""
CLASS_INFO_QUERY = """
    SELECT c.id, c.class, c.subject, c.join_code, p.name AS professor_name
    FROM TC.class c JOIN TC.professor_profile p ON p.user_id = c.professor_id
    WHERE c.id = %s
"""
CLASS_ITEMS_GET_QUERY = """
    SELECT ci.id, ci.created_at, ci.title, AVG(r.value) AS avg_rating, COUNT(r.id) AS rating_count,
           COALESCE(MAX(r.student_id = %s), 0) AS rated_by_user
    FROM TC.class_item ci
    LEFT JOIN TC.rating r ON r.class_item_id = ci.id AND r.active = 1
    WHERE ci.class_id = %s
    GROUP BY ci.id, ci.created_at, ci.title
    ORDER BY ci.created_at
"""
CLASS_BY_JOIN_CODE_QUERY = "SELECT c.id FROM TC.class c WHERE c.join_code = %s AND c.institution_id = %s"
VALIDATE_STUDENT_CLASS_LINK_QUERY = "SELECT id FROM TC.student_class WHERE student_id = %s AND class_id = %s"
