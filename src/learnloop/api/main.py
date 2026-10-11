"""FastAPI Application entry point for LearnLoop AI."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from learnloop.api.routes import router
from learnloop.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema is ready on startup
    init_db()
    yield


app = FastAPI(
    title="LearnLoop AI API",
    description="Adaptive Misconception Detector & Fractions Tutor API",
    version="0.1.0",
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

app.include_router(router)


@app.get("/")
def root():
    return {
        "app": "LearnLoop AI API",
        "status": "online",
        "docs_url": "/docs",
    }
