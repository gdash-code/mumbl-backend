"""
Stub for audio feature extraction (timing, pitch contours, syllable-like chunks).
TODO: implement lightweight feature extraction to feed the lyric generator.
"""

from typing import Any, Dict


def extract_features(file_path: str) -> Dict[str, Any]:
    # TODO: implement feature extraction (pitch, energy, rough timing marks)
    return {"notes": [], "timing": [], "metadata": {}}
