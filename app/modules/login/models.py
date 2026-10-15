_USER_COLUMNS = """
    u.id, u.role, u.institution_id, COALESCE(pp.is_coordinator, 0) AS is_coordinator
    FROM TC.users u LEFT JOIN TC.professor_profile pp ON pp.user_id = u.id
"""

LOGIN_SELECT_USER_QUERY = f"SELECT u.password_hash, {_USER_COLUMNS} WHERE u.email = %s"
LOGIN_SELECT_USER_BY_ID_QUERY = f"SELECT {_USER_COLUMNS} WHERE u.id = %s"
UPDATE_PASSWORD_HASH_QUERY = "UPDATE TC.users SET password_hash = %s WHERE id = %s"
