from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.database import lifespan
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from app.modules.authenticate.router import router as authenticate_router
from app.modules.institution.router import router as institution_router
from app.modules.login.router import router as login_router
from app.modules.feedback.router import router as feedback_router
from app.modules.me.router import router as me_router

app = FastAPI(title="TrueClass API", lifespan=lifespan, redirect_slashes=False)

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="192.168.15.124")

@app.middleware("http")
async def require_json_post(request: Request, call_next):
    content_type = request.headers.get("content-type", "")
    if request.method == "POST" and not content_type.startswith("application/json"):
        return JSONResponse(status_code=415, content={"detail": "Content-Type deve ser application/json"})
    return await call_next(request)

# Incluindo as rotas que criamos
app.include_router(authenticate_router)
app.include_router(institution_router)
app.include_router(login_router)
app.include_router(feedback_router)
app.include_router(me_router)

@app.get("/ping")
def read_root():
    return {"message": "Pong"}
