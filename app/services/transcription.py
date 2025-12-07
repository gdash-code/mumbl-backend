from whisper_transcriber import transcribe_audio


def transcribe_file(file_path: str) -> str:
    """
    Thin wrapper around whisper_transcriber.transcribe_audio.
    """
    return transcribe_audio(file_path)
