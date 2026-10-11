"""Aggregate router for LearnLoop AI API version 1 (/api/v1)."""

from fastapi import APIRouter

from learnloop.api.v1.assessments import router as assessments_router
from learnloop.api.v1.lessons import router as lessons_router
from learnloop.api.v1.progress import router as progress_router
from learnloop.api.v1.sessions import router as sessions_router
from learnloop.api.v1.tutoring import router as tutoring_router
from learnloop.api.v1.voice import router as voice_router

router = APIRouter(prefix="/api/v1")

router.include_router(sessions_router)
router.include_router(lessons_router)
router.include_router(assessments_router)
router.include_router(progress_router)
router.include_router(tutoring_router)
router.include_router(voice_router)


@router.get("/health", tags=["health"])
def api_v1_health():
    """Sanitized health check for API v1."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "api_prefix": "/api/v1",
    }
