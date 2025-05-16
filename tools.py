import logging, subprocess, requests
from app.config import settings
import zipfile
import fitz
from pathlib import Path
import aiofiles

logger = logging.getLogger("gala.tools")

# --- Imagenes ---
def handle_image(prompt: str) -> str:
    text = prompt.removeprefix("/imagen").strip()
    if not text:
        return "❗ Debes escribir algo después de `/imagen`."

    # Moderación
    try:
        mod = requests.post(
            "https://api.openai.com/v1/moderations",
            headers={"Authorization":f"Bearer {settings.OPENAI_API_KEY}"},
            json={"input": text},
            timeout=10
        ).json()
        if mod["results"][0]["flagged"]:
            return "❌ No puedo generar esa imagen por política de contenido."
    except Exception as e:
        logger.warning("Moderación falló, intentando de todas formas: %s", e)

    # Generación DALL·E-2
    payload = {
        "model": "dall-e-2",
        "prompt": text,
        "n": settings.IMAGE_COUNT,
        "size": settings.IMAGE_SIZE,
        "response_format": "url"
    }
    try:
        r = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={
              "Authorization":f"Bearer {settings.OPENAI_API_KEY}",
              "Content-Type":"application/json"
            },
            json=payload,
            timeout=30
        )
        if r.status_code != 200:
            return "❌ Error generando imagen: " + (r.json().get("error", r.text))
        return r.json()["data"][0]["url"]
    except Exception as e:
        logger.exception("Image API error")
        return f"❌ Error generando imagen: {e}"

# --- Código ---
def handle_code(prompt: str) -> str:
    code = prompt.removeprefix("/codigo").strip()
    if not code:
        return "❗ Usa `/codigo tu_codigo`."
    try:
        res = subprocess.run(
            ["python","-c",code],
            capture_output=True, text=True, timeout=10
        )
        out = res.stdout.strip() or res.stderr.strip()
        return out or "✅ Ejecutado sin output."
    except subprocess.TimeoutExpired:
        return "❌ Tiempo de ejecución excedido."
    except Exception as e:
        return f"❌ Error en ejecución: {e}"

# --- PDF ---
def handle_pdf(file_path: str) -> str:
    try:
        doc = fitz.open(file_path)
        txt = "".join(p.get_text() for p in doc)
        doc.close()
        return txt[:2000] + ("...[truncado]" if len(txt)>2000 else "")
    except Exception as e:
        logger.exception("PDF error")
        return f"❌ Error procesando PDF: {e}"
