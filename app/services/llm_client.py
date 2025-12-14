"""
Stub LLM client. Wire to Cohere/OpenAI/etc. when ready.
"""
from typing import Dict, Optional


class LLMClient:
    def __init__(self, provider: str, api_key: Optional[str], model: str):
        self.provider = provider
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, extra: Optional[Dict] = None) -> Dict:
        """
        TODO: implement provider-specific call. For now return a mock payload.
        TODO: add Cohere implementation (chat vs generate), map response to sections.
        TODO: handle auth errors and timeouts gracefully.
        """
        return {
            "provider": self.provider,
            "model": self.model,
            "prompt_preview": prompt[:200],
            "output": {
                "verse": ["TODO: implement LLM call"],
                "chorus": ["TODO: implement LLM call"],
            },
        }
