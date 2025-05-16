from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.memory import memory
from app.services.tools import handle_image, handle_code, handle_pdf
from openai import OpenAI
from app.config import settings
import logging

logger = logging.getLogger("gala.chat")
router = APIRouter()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

@router.websocket("/ws/chat")
async def ws_chat(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_json()
            prompt = msg.get("prompt","").strip()
            if not prompt:
                continue

            memory.save("user", prompt)

            # IMAGEN
            if prompt.startswith("/imagen"):
                res = handle_image(prompt)
                if res.startswith("http"):
                    await ws.send_json({"type":"image","url":res})
                else:
                    await ws.send_json({"type":"error","message":res})
                continue

            # CÓDIGO
            if prompt.startswith("/codigo"):
                out = handle_code(prompt)
                await ws.send_json({"role":"assistant","content":out})
                memory.save("assistant", out)
                continue

            # PDF
            if prompt.startswith("/pdf"):
                out = handle_pdf(prompt.removeprefix("/pdf").strip())
                await ws.send_json({"role":"assistant","content":out})
                memory.save("assistant", out)
                continue

            # CHAT
            ctx = memory.load_context()
            messages = ctx + [{"role":"user","content":prompt}]
            stream = client.chat.completions.create(
                model=settings.MODEL,
                messages=messages,
                temperature=settings.TEMPERATURE,
                stream=True
            )

            full = ""
            for chunk in stream:
                delta = getattr(chunk.choices[0].delta, "content", "")
                if delta:
                    full += delta
                    await ws.send_json({"role":"assistant","content":delta,"stream":True})
            memory.save("assistant", full)

    except WebSocketDisconnect:
        logger.info("WebSocket desconectado")
    except Exception as e:
        logger.exception("WS error")
        await ws.close(code=1011)
