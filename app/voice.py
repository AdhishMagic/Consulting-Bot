from fastapi import APIRouter, UploadFile, File
import os
from .utils import create_response
from datetime import datetime

router = APIRouter(prefix="/voice", tags=["Voice"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_voice(audio: UploadFile = File(...)):
    """Accepts an audio file blob from the frontend and stores it.
    Returns basic metadata for UI confirmation.
    """
    try:
        # Construct safe filename with timestamp
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        original_name = os.path.basename(audio.filename)
        stored_name = f"voice_{ts}_{original_name}" if original_name else f"voice_{ts}.webm"
        path = os.path.join(UPLOAD_DIR, stored_name)

        contents = await audio.read()
        with open(path, "wb") as f:
            f.write(contents)

        meta = {
            "filename": stored_name,
            "original_filename": original_name,
            "size_bytes": len(contents),
            "content_type": audio.content_type,
            "stored_path": path,
        }
        return create_response(success=True, data={"audio": meta})
    except Exception as e:
        return create_response(success=False, error="Upload failed", details={"message": str(e)})
