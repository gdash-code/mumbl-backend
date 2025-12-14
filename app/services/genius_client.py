"""
Stub Genius API client for metadata (not lyrics) to stay copyright-safe.
"""
from typing import Dict, List, Optional


class GeniusClient:
    def __init__(self, token: Optional[str]):
        self.token = token

    def fetch_song_metadata(self, query: str) -> List[Dict]:
        """
        TODO: call Genius search endpoint and return metadata only (artist, genre/tags, year).
        """
        if not self.token:
            return []
        return []
