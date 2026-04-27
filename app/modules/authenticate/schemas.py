from pydantic import BaseModel

# Resposta ao POST
class AuthenticateResponse(BaseModel):
    access_token: str
    token_type: str

    model_config = {
        "from_attributes": True
    }