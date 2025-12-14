from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.models.lyrics import LyricsRequest
from app.services.genius_client import GeniusClient
from app.services.llm_client import LLMClient
from app.services.lyrics_service import LyricsService

router = APIRouter()


@router.post("/lyrics/generate")
async def generate_lyrics(payload: LyricsRequest):
    """
    Stub endpoint for lyric generation. Wires Genius + LLM clients with TODOs.
    """
    try:
        # TODO: cache Genius/LLM clients instead of recreating per request
        # TODO: accept transcript/audio_features from frontend to guide generation
        genius = GeniusClient(settings.genius_token)
        llm = LLMClient(settings.llm_provider, settings.llm_api_key, settings.llm_model)
        service = LyricsService(genius, llm)
        return service.generate(payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
