from fastapi import FastAPI

from app.api import routes_audio, routes_lyrics
from app.core.config import settings
from app.core.cors import setup_cors
from app.core.rate_limit import RateLimitMiddleware
from app.utils.storage import ensure_upload_dir


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
    )

    setup_cors(app, settings.frontend_origin)

    app.add_middleware(
        RateLimitMiddleware,
        max_requests=settings.rate_limit_per_minute,
        window_seconds=60,
    )

    ensure_upload_dir(settings.upload_dir)

    app.include_router(routes_audio.router)
    app.include_router(routes_lyrics.router)

    return app
