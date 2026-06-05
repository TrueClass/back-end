from fastapi import FastAPI
from app.core.database import lifespan
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from app.modules.authenticate.router import router as authenticate_router
from app.modules.institution.router import router as institution_router
from app.modules.login.router import router as login_router
from app.modules.feedback.router import router as feedback_router

app = FastAPI(title="TrueClass API", lifespan=lifespan, redirect_slashes=False)

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="192.168.15.124")

# Incluindo as rotas que criamos
app.include_router(authenticate_router)
app.include_router(institution_router)
app.include_router(login_router)
app.include_router(feedback_router)

@app.get("/ping")
def read_root():
    return {"message": "Pong"}