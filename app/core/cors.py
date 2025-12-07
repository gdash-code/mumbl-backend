# app/core/cors.py
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app, allowed_origin: str) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[allowed_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
