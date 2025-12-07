"""
Lyric generation orchestration.
"""
from app.models.lyrics import LyricsRequest, LyricsResponse
from app.services.genius_client import GeniusClient
from app.services.llm_client import LLMClient
from app.services.prompt_builder import build_prompt


class LyricsService:
    def __init__(self, genius: GeniusClient, llm: LLMClient):
        self.genius = genius
        self.llm = llm

    def generate(self, payload: LyricsRequest) -> LyricsResponse:
        # TODO: fetch Genius metadata based on payload.example_artists or topic
        genius_tags = []
        prompt = build_prompt(payload, genius_tags)

        # TODO: translate payload.audio_features into prompt constraints
        llm_output = self.llm.generate(prompt)

        return LyricsResponse(
            prompt_used=prompt,
            sections=llm_output.get("output", {}),
            provider=llm_output.get("provider"),
            model=llm_output.get("model"),
        )
