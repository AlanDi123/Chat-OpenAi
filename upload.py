from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import zipfile, aiofiles
from app.config import settings

router = APIRouter()

@router.post("/upload", summary="Sube ZIP/TXT u otros")
async def upload_file(file: UploadFile = File(...)):
    up = Path(settings.UPLOAD_FOLDER)
    up.mkdir(parents=True, exist_ok=True)
    dest = up / file.filename

    # Guardado asíncrono
    try:
        async with aiofiles.open(dest, "wb") as f:
            await f.write(await file.read())
    except Exception as e:
        raise HTTPException(500, f"Error guardando: {e}")

    # ZIP
    if file.filename.lower().endswith(".zip"):
        try:
            with zipfile.ZipFile(dest, "r") as z:
                z.extractall(up)
            return JSONResponse({"message":f"ZIP extraído en {up}"})
        except zipfile.BadZipFile:
            raise HTTPException(400,"ZIP inválido")
    # TXT
    if file.filename.lower().endswith(".txt"):
        async with aiofiles.open(dest, "r", encoding="utf-8") as f:
            text = await f.read(2000)
        return JSONResponse({"message":text})

    return JSONResponse({"message":f"Subido {file.filename}"})
