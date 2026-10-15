from fastapi import Response

ACCESS_TOKEN_MAX_AGE = 1800
REFRESH_TOKEN_MAX_AGE = 604800

COOKIE_OPTIONS = {"httponly": True, "secure": True, "samesite": "none"}

def set_access_cookie(response: Response, token: str):
    response.set_cookie(key="access_token", value=token, max_age=ACCESS_TOKEN_MAX_AGE, **COOKIE_OPTIONS)

def set_refresh_cookie(response: Response, token: str):
    response.set_cookie(key="refresh_token", value=token, max_age=REFRESH_TOKEN_MAX_AGE, **COOKIE_OPTIONS)

def clear_auth_cookies(response: Response):
    response.delete_cookie("access_token", **COOKIE_OPTIONS)
    response.delete_cookie("refresh_token", **COOKIE_OPTIONS)
