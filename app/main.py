from fastapi import FastAPI
from app.modules.institution.router import router as institution_router
from app.modules.login.router import router as login_router

app = FastAPI(title="TrueClass API")

# Incluindo as rotas que criamos
app.include_router(institution_router)
app.include_router(login_router)

@app.get("/ping")
def read_root():
    return {"message": "Pong"}