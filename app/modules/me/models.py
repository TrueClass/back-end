ME_SELECT_QUERY = """
    SELECT u.id, u.email, u.role, pp.name, pp.rating, pp.profile_picture, pp.is_coordinator
    FROM TC.users u
    LEFT JOIN TC.professor_profile pp ON u.id = pp.user_id
    WHERE u.id = %s
"""
