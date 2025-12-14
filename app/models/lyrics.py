from typing import Dict, List, Optional

from pydantic import BaseModel

from app.models.audio import AudioFeatures


class LyricsRequest(BaseModel):
    topic: Optional[str] = None
    mood: Optional[str] = None
    tempo: Optional[str] = None
    example_artists: List[str] = []
    audio_features: Optional[AudioFeatures] = None
    extra_instructions: Optional[str] = None


class LyricsResponse(BaseModel):
    sections: Dict[str, List[str]]
    prompt_used: str
    provider: Optional[str] = None
    model: Optional[str] = None
