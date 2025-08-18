# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os, uuid

from whisper_transcriber import transcribe_audio

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def _save_upload(file: UploadFile) -> str:
    file_id = f"{uuid.uuid4()}_{file.filename}"
    dst = os.path.join(UPLOAD_DIR, file_id)

    # rewind in case the stream was peeked
    try:
        file.file.seek(0)
    except Exception:
        pass

    with open(dst, "wb") as out:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

    size = os.path.getsize(dst)
    if size < 1024:
        raise HTTPException(status_code=400, detail=f"Uploaded file too small ({size} bytes)")
    return dst

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        raw_path = _save_upload(file)
        text = transcribe_audio(raw_path)
        return {"transcript": text}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
