PROFESSOR_INSERT_QUERY = "INSERT INTO TC.users (institution_id, email, password_hash, role) VALUES (%s, %s, %s, %s)"
PROFESSOR_PROFILE_INSERT_QUERY = "INSERT INTO TC.professor_profile (user_id, name, is_coordinator) VALUES (%s, %s, %s)"
CHECK_COORDINATOR_QUERY = "SELECT pp.is_coordinator FROM TC.users u JOIN TC.professor_profile pp ON u.id = pp.user_id WHERE u.id = %s AND u.institution_id = %s AND pp.is_coordinator = 1"
COORDINATOR_PROFESSOR_INSERT_QUERY = "INSERT INTO TC.coordinator_professor (professor_id, coordinator_id) VALUES (%s, %s)"

_PROFESSOR_COLUMNS = "u.id, pp.name, pp.rating, u.email, pp.profile_picture, pp.is_coordinator"

PROFESSOR_GET_QUERY = f"SELECT {_PROFESSOR_COLUMNS} FROM TC.users u JOIN TC.professor_profile pp ON u.id = pp.user_id WHERE u.institution_id = %s AND u.role IN ('professor', 'coordinator') ORDER BY pp.name LIMIT %s OFFSET %s"
PROFESSOR_COUNT_QUERY = "SELECT COUNT(*) as count FROM TC.users WHERE institution_id = %s AND role IN ('professor', 'coordinator')"
PROFESSOR_PROFILE_QUERY = f"SELECT {_PROFESSOR_COLUMNS} FROM TC.users u JOIN TC.professor_profile pp ON u.id = pp.user_id WHERE u.id = %s AND u.institution_id = %s AND u.role IN ('professor', 'coordinator')"
PROFESSORS_BY_COORDINATOR_QUERY = f"""
    SELECT {_PROFESSOR_COLUMNS}
    FROM TC.coordinator_professor cp
    JOIN TC.users u ON u.id = cp.professor_id
    JOIN TC.professor_profile pp ON pp.user_id = u.id
    WHERE cp.coordinator_id = %s AND u.institution_id = %s
    ORDER BY pp.name
"""
IS_SUPERVISOR_QUERY = "SELECT 1 FROM TC.coordinator_professor WHERE professor_id = %s AND coordinator_id = %s"

PROFESSOR_CLASSES_QUERY = """
    SELECT c.id, c.class, c.subject,
           MAX(CASE WHEN ci.created_at < %s THEN ci.created_at END) AS last_class,
           MIN(CASE WHEN ci.created_at >= %s THEN ci.created_at END) AS next_class,
           (SELECT AVG(r.value) FROM TC.rating r JOIN TC.class_item ri ON ri.id = r.class_item_id
            WHERE ri.class_id = c.id AND r.active = 1) AS avg_rating,
           (SELECT COUNT(*) FROM TC.rating r JOIN TC.class_item ri ON ri.id = r.class_item_id
            WHERE ri.class_id = c.id AND r.active = 1) AS rating_count
    FROM TC.class c
    LEFT JOIN TC.class_item ci ON ci.class_id = c.id
    WHERE c.professor_id = %s
    GROUP BY c.id, c.class, c.subject
    ORDER BY c.subject
"""

_FEEDBACK_BASE = """
    SELECT r.id, r.value, r.content, r.boosts, r.created_at, c.subject, ci.title
    FROM TC.rating r
    JOIN TC.class_item ci ON ci.id = r.class_item_id
    JOIN TC.class c ON c.id = ci.class_id
    WHERE c.professor_id = %s AND r.active = 1
"""
FEEDBACKS_MOST_BOOSTED_QUERY = _FEEDBACK_BASE + " ORDER BY r.boosts DESC, r.created_at DESC LIMIT %s"
FEEDBACKS_HIGHEST_QUERY = _FEEDBACK_BASE + " ORDER BY r.value DESC, r.boosts DESC LIMIT %s"
FEEDBACKS_LOWEST_QUERY = _FEEDBACK_BASE + " ORDER BY r.value ASC, r.boosts DESC LIMIT %s"

_PROFESSOR_RATINGS = """
    FROM TC.rating r
    JOIN TC.class_item ci ON ci.id = r.class_item_id
    JOIN TC.class c ON c.id = ci.class_id
    WHERE c.professor_id = %s AND r.active = 1
"""

PROFESSOR_RATINGS_COUNT = "SELECT COUNT(*) AS count" + _PROFESSOR_RATINGS

PROFESSOR_THEMES = """
    SELECT ai_themes, ai_themes_rating_count, ai_themes_created_at,
           CASE
               WHEN ai_themes_requested_at IS NOT NULL
                AND ai_themes_requested_at > NOW() - INTERVAL %s SECOND THEN 1
               ELSE 0
           END AS generating
    FROM TC.professor_profile WHERE user_id = %s
"""

CLAIM_THEMES_GENERATION = """
    UPDATE TC.professor_profile SET ai_themes_requested_at = NOW()
    WHERE user_id = %s
      AND (ai_themes_requested_at IS NULL OR ai_themes_requested_at <= NOW() - INTERVAL %s SECOND)
"""

RELEASE_THEMES_GENERATION = "UPDATE TC.professor_profile SET ai_themes_requested_at = NULL WHERE user_id = %s"

UPDATE_PROFESSOR_THEMES = """
    UPDATE TC.professor_profile
    SET ai_themes = %s, ai_themes_rating_count = %s, ai_themes_created_at = %s, ai_themes_requested_at = NULL
    WHERE user_id = %s
"""

RATINGS_PENDING_ASPECTS = "SELECT r.id, r.content" + _PROFESSOR_RATINGS + " AND r.aspects_extracted_at IS NULL ORDER BY r.id"

INSERT_RATING_ASPECT = """
    INSERT INTO TC.rating_aspect (rating_id, sentiment, evidence_start, evidence_end, aspect)
    VALUES (%s, %s, %s, %s, %s)
"""

MARK_ASPECTS_EXTRACTED = "UPDATE TC.rating SET aspects_extracted_at = NOW() WHERE id = %s"

ASPECTS_PENDING_EMBEDDING = """
    SELECT ra.id, ra.aspect
    FROM TC.rating_aspect ra
    JOIN TC.rating r ON r.id = ra.rating_id
    JOIN TC.class_item ci ON ci.id = r.class_item_id
    JOIN TC.class c ON c.id = ci.class_id
    WHERE c.professor_id = %s AND r.active = 1
      AND (ra.embedding IS NULL OR ra.embedding_model <> %s)
"""

UPDATE_ASPECT_EMBEDDING = "UPDATE TC.rating_aspect SET embedding = %s, embedding_model = %s WHERE id = %s"

PROFESSOR_ASPECTS = """
    SELECT ra.aspect, ra.sentiment, ra.evidence_start, ra.evidence_end, ra.embedding,
           r.id AS rating_id, r.content, r.boosts, c.subject, ci.title
    FROM TC.rating_aspect ra
    JOIN TC.rating r ON r.id = ra.rating_id
    JOIN TC.class_item ci ON ci.id = r.class_item_id
    JOIN TC.class c ON c.id = ci.class_id
    WHERE c.professor_id = %s AND r.active = 1 AND ra.embedding_model = %s
    ORDER BY r.boosts DESC, r.id DESC
"""
