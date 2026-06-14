CHECK_CLASS_ITEM_EXISTS = """
    SELECT ci.id, c.professor_id
    FROM TC.class_item ci JOIN TC.class c ON ci.class_id = c.id
    WHERE ci.id = %s
"""

CHECK_STUDENT_ENROLLED = """
    SELECT sc.id FROM TC.student_class sc
    JOIN TC.class_item ci ON ci.class_id = sc.class_id
    WHERE sc.student_id = %s AND ci.id = %s
"""

CHECK_ALREADY_RATED = """
    SELECT id FROM TC.rating
    WHERE student_id = %s AND class_item_id = %s
"""

RATING_INSERT = """
    INSERT INTO TC.rating (student_id, class_item_id, content, value, active)
    VALUES (%s, %s, %s, %s, 1)
"""

UPDATE_PROFESSOR_RATING = """
    UPDATE TC.professor_profile
    SET rating = (
        SELECT AVG(r.value) FROM TC.rating r
        JOIN TC.class_item ci ON r.class_item_id = ci.id
        JOIN TC.class c ON ci.class_id = c.id
        WHERE c.professor_id = %s AND r.active = 1
    )
    WHERE user_id = %s
"""

RATINGS_BY_CLASS_ITEM = """
    SELECT id, content, value, boosts, created_at, IF(student_id = %s, 1, 0) AS sent_by_user
    FROM TC.rating
    WHERE class_item_id = %s AND active = 1
    LIMIT %s OFFSET %s
"""

RATINGS_COUNT = """
    SELECT COUNT(*) as count FROM TC.rating
    WHERE class_item_id = %s AND active = 1
"""

CHECK_RATING_EXISTS = "SELECT id FROM TC.rating WHERE id = %s AND active = 1"

CHECK_BOOST_EXISTS = "SELECT id FROM TC.rating_boost WHERE student_id = %s AND rating_id = %s"

INSERT_BOOST = "INSERT INTO TC.rating_boost (student_id, rating_id) VALUES (%s, %s)"

DELETE_BOOST = "DELETE FROM TC.rating_boost WHERE student_id = %s AND rating_id = %s"

INCREMENT_BOOSTS = "UPDATE TC.rating SET boosts = boosts + 1 WHERE id = %s"

DECREMENT_BOOSTS = "UPDATE TC.rating SET boosts = boosts - 1 WHERE id = %s"

GET_BOOST_COUNT = "SELECT boosts FROM TC.rating WHERE id = %s"
