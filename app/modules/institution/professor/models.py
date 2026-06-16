# --- INSERT Queries ---
PROFESSOR_INSERT_QUERY = "INSERT INTO TC.users (institution_id, email, password_hash, role) VALUES (%s, %s, %s, %s)"
PROFESSOR_PROFILE_INSERT_QUERY = "INSERT INTO TC.professor_profile (user_id, name, is_coordinator) VALUES (%s, %s, %s)"
COORDINATOR_PROFESSOR_INSERT_QUERY = "INSERT INTO TC.coordinator_professor (professor_id, coordinator_id) VALUES (%s, %s)"

# --- GET Queries ---
CHECK_COORDINATOR_QUERY = "SELECT pp.is_coordinator FROM TC.users u JOIN TC.professor_profile pp ON u.id = pp.user_id WHERE u.id = %s AND pp.is_coordinator = 1"
PROFESSOR_COUNT_QUERY = "SELECT COUNT(*) as count FROM TC.users WHERE institution_id = %s AND role = 'professor'"
PROFESSOR_GET_QUERY = "SELECT u.id, pp.name, pp.rating, u.email, pp.profile_picture, pp.is_coordinator FROM TC.users u JOIN TC.professor_profile pp ON u.id = pp.user_id WHERE u.institution_id = %s AND u.role = 'professor' LIMIT %s OFFSET %s"

PROFESSOR_COUNT_BY_COORDINATOR = "SELECT COUNT(*) AS count FROM professor_profile pp RIGHT JOIN coordinator_professor cp ON pp.user_id = cp.professor_id WHERE coordinator_id = %s;"
PROFESSOR_GET_BY_COORDINATOR = "SELECT u.id, pp.name, pp.rating, u.email, pp.profile_picture, pp.is_coordinator FROM TC.users u JOIN TC.professor_profile pp ON u.id = pp.user_id RIGHT JOIN TC.coordinator_professor cp ON u.id = cp.professor_id WHERE u.institution_id = %s AND cp.coordinator_id = %s LIMIT %s OFFSET %s"

PROFESSOR_CLASSES_BY_ID = """
    SELECT c.id, c.class, c.subject,
           MAX(CASE WHEN ci.created_at < %s THEN ci.created_at END) AS last_class,
           MIN(CASE WHEN ci.created_at >= %s THEN ci.created_at END) AS next_class
    FROM TC.class c
    JOIN TC.class_item ci ON c.id = ci.class_id
    JOIN TC.users u ON c.professor_id = u.id
    WHERE c.professor_id = %s AND u.institution_id = %s
    GROUP BY c.id, c.class, c.subject
"""

PROFESSOR_FEEDBACKS_MOST_BOOSTED = """
    SELECT r.id, r.content, r.value, r.boosts, r.created_at
    FROM TC.rating r
    JOIN TC.class_item ci ON r.class_item_id = ci.id
    JOIN TC.class c ON ci.class_id = c.id
    JOIN TC.users u ON c.professor_id = u.id
    WHERE c.professor_id = %s AND u.institution_id = %s AND r.active = 1
    ORDER BY r.boosts DESC
    LIMIT %s
"""

PROFESSOR_FEEDBACKS_HIGHEST_RATING = """
    SELECT r.id, r.content, r.value, r.boosts, r.created_at
    FROM TC.rating r
    JOIN TC.class_item ci ON r.class_item_id = ci.id
    JOIN TC.class c ON ci.class_id = c.id
    JOIN TC.users u ON c.professor_id = u.id
    WHERE c.professor_id = %s AND u.institution_id = %s AND r.active = 1
    ORDER BY r.value DESC, r.boosts DESC
    LIMIT %s
"""

PROFESSOR_FEEDBACKS_LOWEST_RATING = """
    SELECT r.id, r.content, r.value, r.boosts, r.created_at
    FROM TC.rating r
    JOIN TC.class_item ci ON r.class_item_id = ci.id
    JOIN TC.class c ON ci.class_id = c.id
    JOIN TC.users u ON c.professor_id = u.id
    WHERE c.professor_id = %s AND u.institution_id = %s AND r.active = 1
    ORDER BY r.value ASC, r.boosts DESC
    LIMIT %s
"""