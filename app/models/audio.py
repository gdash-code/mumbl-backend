from pydantic import BaseModel


class AudioFeatures(BaseModel):
    # TODO: expand with timing, pitch, energy contours
    notes: list[str] = []
    timing: list[float] = []
    metadata: dict = {}
