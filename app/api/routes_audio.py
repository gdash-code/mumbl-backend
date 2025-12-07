from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.services.transcription import transcribe_file
from app.utils.storage import ensure_upload_dir, save_upload

router = APIRouter()


@router.get("/health")
def health():
    return {"ok": True}


@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        ensure_upload_dir(settings.upload_dir)
        raw_path = save_upload(file, settings.upload_dir, min_bytes=settings.min_upload_bytes)
        text = transcribe_file(raw_path)
        return {"transcript": text}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
