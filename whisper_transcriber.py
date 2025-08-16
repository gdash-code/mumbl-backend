# whisper_transcriber.py

import openai
import os
import whisper

# api mode
# openai.api_key = os.getenv("OPENAI_API_KEY")

# def transcribe_audio(file_path: str) -> str:
#     with open(file_path, "rb") as audio_file:
#         transcript = openai.Audio.transcribe("whisper-1", audio_file)
#         return transcript.get("text", "")

# local mode
model = whisper.load_model("base")  # or "small", "medium"

def transcribe_audio(file_path: str) -> str:
    result = model.transcribe(file_path)
    return result.get("text", "")