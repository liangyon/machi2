from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.db.database import init_db
from app.api.routes import auth, runs, grimoire

# ─── Rate limiter ─────────────────────────────────────────────────────────────
# Uses the client's IP address as the rate-limit key.
# Individual route limits are declared with @limiter.limit() decorators.
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Arcane Depths API",
    version="0.1.0",
    lifespan=lifespan,
)

# Attach rate limiter state and its 429 error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,               # required for HttpOnly cookie auth
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(runs.router, prefix="/api/run", tags=["runs"])
app.include_router(grimoire.router, prefix="/api/grimoire", tags=["grimoire"])


@app.get("/health")
async def health():
    return {"status": "ok"}


def dev():
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
