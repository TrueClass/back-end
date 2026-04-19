from fastapi import FastAPI
from app.core.database import lifespan
from app.modules.authenticate.router import router as authenticate_router
from app.modules.institution.router import router as institution_router
from app.modules.login.router import router as login_router

app = FastAPI(title="TrueClass API", lifespan=lifespan)

# Incluindo as rotas que criamos
app.include_router(authenticate_router)
app.include_router(institution_router)
app.include_router(login_router)

@app.get("/ping")
def read_root():
    return {"message": "Pong"}