# Compatibility shim: import settings from the new app.core.config module.
from app.core.config import Settings, settings

__all__ = ["Settings", "settings"]
