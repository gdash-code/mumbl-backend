from typing import Optional

from pydantic import BaseModel


class GeniusMetadata(BaseModel):
    artist: Optional[str] = None
    title: Optional[str] = None
    year: Optional[int] = None
    tags: list[str] = []
