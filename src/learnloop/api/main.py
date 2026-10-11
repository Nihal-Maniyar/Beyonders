import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Ensure src directory is in sys.path
_src_dir = str(Path(__file__).resolve().parent.parent.parent)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from learnloop.api.routes import router as legacy_router
from learnloop.api.v1 import v1_router
from learnloop.db.seed import seed_database
from learnloop.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema is ready and seeded on startup
    init_db()
    try:
        seed_database()
    except Exception:
        pass
    yield


from learnloop.config import settings

app = FastAPI(
    title="LearnLoop AI API",
    description="Adaptive Misconception Detector & Fractions Tutor API",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS origins (supports comma-separated list or * via CORS_ORIGINS)
cors_origins_env = settings.cors_origins.strip()
if cors_origins_env == "*":
    allow_origins = ["*"]
elif cors_origins_env:
    allow_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
else:
    allow_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_envelope_handler(request, exc: HTTPException):
    """Enforce standard error envelope conforming to context.md Section 22."""
    from fastapi.responses import JSONResponse

    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    elif isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": "HTTP_ERROR", "message": str(exc.detail), "details": []}},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
                "details": [],
            }
        },
    )


app.include_router(v1_router)
app.include_router(legacy_router)


@app.get("/health", tags=["health"])
def health():
    """Root health check for cloud load balancers and deployment probes."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "app": "LearnLoop AI",
    }


@app.get("/")
def root():
    return {
        "app": "LearnLoop AI API",
        "status": "online",
        "docs_url": "/docs",
        "health_url": "/health",
        "api_v1_url": "/api/v1",
    }


# Optional unified deployment: serve built React frontend from /studio if frontend/dist exists
_frontend_dist = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "dist"
if _frontend_dist.exists() and (_frontend_dist / "index.html").exists():
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles

    _assets_dir = _frontend_dist / "assets"
    if _assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(_assets_dir)), name="assets")

    @app.get("/studio", response_class=FileResponse)
    @app.get("/studio/{path:path}", response_class=FileResponse)
    def serve_frontend_studio(path: str = ""):
        return FileResponse(str(_frontend_dist / "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "learnloop.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
