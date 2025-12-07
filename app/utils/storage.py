import os

from fastapi import HTTPException, UploadFile


def ensure_upload_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def save_upload(file: UploadFile, upload_dir: str, min_bytes: int = 1024) -> str:
    file_id = f"{os.getpid()}_{file.filename}"
    dst = os.path.join(upload_dir, file_id)

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
    if size < min_bytes:
        raise HTTPException(status_code=400, detail=f"Uploaded file too small ({size} bytes)")
    return dst
