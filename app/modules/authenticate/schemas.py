from pydantic import BaseModel

# O que recebemos pelo POST
class AuthenticateResponse(BaseModel):
    message: str