"""
Prompt builder for lyric generation.
"""
from app.models.lyrics import LyricsRequest


def build_prompt(payload: LyricsRequest, genius_tags: list[str] | None = None) -> str:
    """
    TODO: enrich prompt with phonetic/timing hints and Genius metadata tags.
    """
    tags = ", ".join(genius_tags or [])
    return (
        "You are a lyricist. Create original lyrics (do not copy existing songs).\n"
        f"Topic: {payload.topic or 'unspecified'}\n"
        f"Mood: {payload.mood or 'unspecified'}\n"
        f"Tempo: {payload.tempo or 'unspecified'}\n"
        f"Style inspirations: {', '.join(payload.example_artists or [])}\n"
        f"Genius tags: {tags}\n"
        "Return verses and choruses as short lines."
    )
