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


app = FastAPI(
    title="LearnLoop AI API",
    description="Adaptive Misconception Detector & Fractions Tutor API",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
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


@app.get("/")
def root():
    return {
        "app": "LearnLoop AI API",
        "status": "online",
        "docs_url": "/docs",
    }
