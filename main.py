"""
IRIS - Backend unificado en un solo puerto
-------------------------------------------
- WebSocket  ws://host/ws         → web (fragmentos en tiempo real)
- HTTP POST  http://host/transcribir → Cordova (archivo completo)

Todo corre en el mismo puerto asignado por Railway via PORT.

Uso local:
    python3 main.py

Uso Railway:
    Procfile: web: python3 main.py
"""

import asyncio
import os
import logging
import datetime
import tempfile
import websockets
import whisper
from aiohttp import web

# Configuración 
PORT  = int(os.environ.get("PORT", 8765))
HOST  = "0.0.0.0"
MODEL = "tiny"
LANG  = "es"

TRANSCRIPCIONES_DIR = "transcripciones"
os.makedirs(TRANSCRIPCIONES_DIR, exist_ok=True)

# Logging 
logging.basicConfig(
    level   = logging.INFO,
    format  = "[%(asctime)s] %(levelname)s - %(message)s",
    datefmt = "%H:%M:%S"
)
log = logging.getLogger("IRIS")

# Carga del modelo 
log.info(f"Cargando modelo Whisper '{MODEL}'...")
modelo = whisper.load_model(MODEL)
log.info("Modelo listo.")

# Utilidades 
def guardar_transcripcion(texto):
    ahora  = datetime.datetime.now()
    nombre = ahora.strftime("transcripcion_%Y-%m-%d_%H-%M-%S.txt")
    ruta   = os.path.join(TRANSCRIPCIONES_DIR, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(f"Fecha: {ahora.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(texto)
    log.info(f"Transcripción guardada en: {ruta}")

def transcribir_archivo(ruta):
    resultado = modelo.transcribe(
        ruta,
        language                   = LANG,
        fp16                       = False,
        condition_on_previous_text = False
    )
    return resultado["text"].strip()

# WebSocket handler (web)
async def ws_handler(websocket):
    cliente    = websocket.remote_address
    fragmentos = []
    textoFinal = ""
    log.info(f"[WS] Cliente conectado: {cliente}")

    try:
        async for mensaje in websocket:
            if isinstance(mensaje, str) and mensaje == "FIN":
                log.info("[WS] Señal FIN recibida.")
                if textoFinal:
                    guardar_transcripcion(textoFinal)
                await websocket.send("(fin)")
                break

            if not isinstance(mensaje, bytes) or len(mensaje) == 0:
                continue

            fragmentos.append(mensaje)
            log.info(f"[WS] Fragmento #{len(fragmentos)}: {len(mensaje)} bytes")

            audio_acumulado = b"".join(fragmentos)
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
                tmp.write(audio_acumulado)
                tmp_path = tmp.name

            try:
                texto = transcribir_archivo(tmp_path)
                if texto:
                    textoFinal = texto
                    log.info(f"[WS] Transcripción parcial: {texto}")
                    await websocket.send(texto)
            except Exception as e:
                log.error(f"[WS] Error en transcripción: {e}")
            finally:
                os.unlink(tmp_path)

    except websockets.exceptions.ConnectionClosedOK:
        log.info(f"[WS] Cliente desconectado: {cliente}")
    except websockets.exceptions.ConnectionClosedError as e:
        log.warning(f"[WS] Conexión cerrada con error: {e}")
    except Exception as e:
        log.error(f"[WS] Error inesperado: {e}")

# HTTP handler (Cordova + upgrade a WS) 
async def http_handler(request):
    # Upgrade a WebSocket si el cliente lo pide
    if request.headers.get("Upgrade", "").lower() == "websocket":
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        # Delega al handler de WebSocket via websockets library
        # (aiohttp maneja WS nativamente aquí)
        fragmentos = []
        textoFinal = ""
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT and msg.data == "FIN":
                if textoFinal:
                    guardar_transcripcion(textoFinal)
                await ws.send_str("(fin)")
                break
            elif msg.type == web.WSMsgType.BINARY and len(msg.data) > 0:
                fragmentos.append(msg.data)
                audio_acumulado = b"".join(fragmentos)
                with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
                    tmp.write(audio_acumulado)
                    tmp_path = tmp.name
                try:
                    texto = transcribir_archivo(tmp_path)
                    if texto:
                        textoFinal = texto
                        await ws.send_str(texto)
                except Exception as e:
                    log.error(f"[WS] Error: {e}")
                finally:
                    os.unlink(tmp_path)
        return ws

    # HTTP POST /transcribir (Cordova)
    if request.path == "/transcribir" and request.method == "POST":
        headers = {
            "Access-Control-Allow-Origin" : "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
        try:
            datos = await request.read()
            if not datos:
                return web.Response(text="Sin audio", status=400, headers=headers)

            log.info(f"[HTTP] Audio recibido: {len(datos)} bytes")
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(datos)
                tmp_path = tmp.name

            try:
                texto = transcribir_archivo(tmp_path)
                if texto:
                    log.info(f"[HTTP] Transcripción: {texto}")
                    guardar_transcripcion(texto)
                    return web.Response(text=texto, status=200, headers=headers)
                else:
                    return web.Response(text="(sin texto)", status=200, headers=headers)
            except Exception as e:
                log.error(f"[HTTP] Error: {e}")
                return web.Response(text=str(e), status=500, headers=headers)
            finally:
                os.unlink(tmp_path)

        except Exception as e:
            return web.Response(text=str(e), status=500)

    # OPTIONS preflight
    if request.method == "OPTIONS":
        return web.Response(headers={
            "Access-Control-Allow-Origin" : "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        })

    return web.Response(text="IRIS Backend OK", status=200)

# Inicio
async def main():
    app = web.Application()
    app.router.add_route("*", "/{path_info:.*}", http_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()

    log.info(f"Servidor IRIS corriendo en puerto {PORT}")
    log.info(f"  WebSocket : ws://host/")
    log.info(f"  HTTP POST : http://host/transcribir")
    log.info("Esperando conexiones...")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
