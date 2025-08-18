# whisper_transcriber.py
import os
from fastapi import HTTPException
from pydub import AudioSegment
from faster_whisper import WhisperModel

# Explicitly point pydub at Homebrew ffmpeg (adjust if your path differs)
AudioSegment.converter = "/opt/homebrew/bin/ffmpeg"

# Load once (choose a size: tiny/base/small/medium/large-v3)
# On CPU, "base" is a good starting point. If you have an NVIDIA GPU, set device="cuda".
MODEL_SIZE = os.getenv("WHISPER_MODEL", "base")
DEVICE = os.getenv("WHISPER_DEVICE", "cpu")        # "cpu" or "cuda"
COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE", "int8")# "int8" on CPU, "float16" on CUDA

model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)

def _to_wav_mono16k(src_path: str) -> str:
    """
    Convert any input (m4a/mp3/wav) to mono 16 kHz WAV.
    Raises HTTPException(400) if ffmpeg decode fails.
    """
    try:
        audio = AudioSegment.from_file(src_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ffmpeg decode failed: {e}")

    dst = src_path.rsplit(".", 1)[0] + "_16k.wav"
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(dst, format="wav")
    return dst

def transcribe_audio(file_path: str) -> str:
    """
    Convert -> transcribe with VAD/small beam. Returns plain text.
    Raise HTTP 500 with readable message on unexpected errors.
    """
    wav_path = _to_wav_mono16k(file_path)

    try:
        segments, info = model.transcribe(
            wav_path,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
            beam_size=5
        )
        text = " ".join(s.text for s in segments).strip()
        return text
    except FileNotFoundError:
        # Most common if ffmpeg path changes
        raise HTTPException(status_code=500, detail="ffmpeg not found on PATH")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
