from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health", operation_id="getHealth")
def health() -> dict[str, str]:
    """Liveness/readiness endpoint — used by Docker HEALTHCHECK and Dokploy."""
    settings = get_settings()
    return {"status": "ok", "environment": settings.environment}
