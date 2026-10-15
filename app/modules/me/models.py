ME_SELECT_QUERY = """
    SELECT u.id, u.email, u.role, u.institution_id, i.name AS institution_name,
           pp.name, pp.rating, pp.profile_picture, pp.is_coordinator
    FROM TC.users u
    JOIN TC.institution i ON i.id = u.institution_id
    LEFT JOIN TC.professor_profile pp ON u.id = pp.user_id
    WHERE u.id = %s
"""
