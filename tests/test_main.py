import io
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

def test_transcribe_success(monkeypatch):
    # Mock transcribe_audio so we don't actually run Whisper in tests
    from whisper_transcriber import transcribe_audio

    def fake_transcribe_audio(path: str) -> str:
        return "this is a fake transcript"

    # Patch the function used inside main
    monkeypatch.setattr("main.transcribe_audio", fake_transcribe_audio)

    # Build a fake file with content > 1KB (so it passes your size check)
    fake_audio_content = b"x" * 2048
    files = {"file": ("test.wav", io.BytesIO(fake_audio_content), "audio/wav")}

    response = client.post("/transcribe", files=files)

    assert response.status_code == 200
    assert response.json() == {"transcript": "this is a fake transcript"}
    
def test_transcribe_small_file_rejected():
    # smaller than 1024 bytes
    tiny_audio_content = b"small"
    files = {"file": ("tiny.wav", io.BytesIO(tiny_audio_content), "audio/wav")}

    response = client.post("/transcribe", files=files)

    assert response.status_code == 400
    body = response.json()
    assert "Uploaded file too small" in body["detail"]    