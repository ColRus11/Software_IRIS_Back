"""
IRIS - Backend WebSocket + HTTP POST + Whisper
-----------------------------------------------
- WebSocket ws://localhost:8765  → web (fragmentos en tiempo real)
- HTTP POST http://localhost:8766/transcribir → Cordova (archivo completo)

Uso:
    python3 main.py

Requisitos:
    pip install -r requirements.txt
    brew install ffmpeg
"""

import asyncio
import websockets
import whisper
import tempfile
import os
import logging
import datetime
from aiohttp import web

# Configuración 
WS_HOST   = "0.0.0.0"
HTTP_HOST = "0.0.0.0"
# Railway asigna el puerto via variable de entorno
HTTP_PORT = int(os.environ.get("PORT", 8766))
WS_PORT   = int(os.environ.get("WS_PORT", 8765))
MODEL     = "base"
LANG      = "es"

TRANSCRIPCIONES_DIR = "transcripciones"
os.makedirs(TRANSCRIPCIONES_DIR, exist_ok=True)

# ─── Logging ──────────────────────────────────────────────
logging.basicConfig(
    level   = logging.INFO,
    format  = "[%(asctime)s] %(levelname)s - %(message)s",
    datefmt = "%H:%M:%S"
)
log = logging.getLogger("IRIS")

# ─── Carga del modelo ─────────────────────────────────────
log.info(f"Cargando modelo Whisper '{MODEL}'...")
modelo = whisper.load_model(MODEL)
log.info("Modelo listo.")

# ─── Utilidades ───────────────────────────────────────────
def guardar_transcripcion(texto):
    ahora  = datetime.datetime.now()
    nombre = ahora.strftime("transcripcion_%Y-%m-%d_%H-%M-%S.txt")
    ruta   = os.path.join(TRANSCRIPCIONES_DIR, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(f"Fecha: {ahora.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(texto)
    log.info(f"Transcripción guardada en: {ruta}")
    return ruta

def transcribir_archivo(ruta):
    resultado = modelo.transcribe(
        ruta,
        language                   = LANG,
        fp16                       = False,
        condition_on_previous_text = False
    )
    return resultado["text"].strip()

# ─── WebSocket handler (web) ──────────────────────────────
async def ws_handler(websocket):
    cliente   = websocket.remote_address
    fragmentos = []
    textoFinal = ""
    log.info(f"[WS] Cliente conectado: {cliente}")

    try:
        async for mensaje in websocket:

            # Señal de fin — guarda y cierra
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

            # Transcribe el audio acumulado completo
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

# ─── HTTP POST handler (Cordova) ──────────────────────────
async def http_transcribir(request):
    log.info("[HTTP] Solicitud de transcripción recibida")

    # Permite solicitudes desde cualquier origen (CORS para Cordova)
    headers = {
        "Access-Control-Allow-Origin"  : "*",
        "Access-Control-Allow-Methods" : "POST, OPTIONS",
        "Access-Control-Allow-Headers" : "Content-Type"
    }

    # Preflight OPTIONS
    if request.method == "OPTIONS":
        return web.Response(headers=headers)

    try:
        datos = await request.read()

        if not datos:
            return web.Response(
                text    = "Sin audio",
                status  = 400,
                headers = headers
            )

        log.info(f"[HTTP] Audio recibido: {len(datos)} bytes")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(datos)
            tmp_path = tmp.name

        try:
            texto = transcribir_archivo(tmp_path)

            if texto:
                log.info(f"[HTTP] Transcripción: {texto}")
                guardar_transcripcion(texto)
                return web.Response(
                    text    = texto,
                    status  = 200,
                    headers = headers
                )
            else:
                return web.Response(
                    text    = "(sin texto detectado)",
                    status  = 200,
                    headers = headers
                )

        except Exception as e:
            log.error(f"[HTTP] Error en transcripción: {e}")
            return web.Response(
                text    = f"Error: {str(e)}",
                status  = 500,
                headers = headers
            )
        finally:
            os.unlink(tmp_path)

    except Exception as e:
        log.error(f"[HTTP] Error inesperado: {e}")
        return web.Response(
            text    = f"Error: {str(e)}",
            status  = 500,
            headers = headers
        )

# ─── Inicio de servidores ─────────────────────────────────
async def main():
    # Servidor WebSocket
    ws_server = await websockets.serve(ws_handler, WS_HOST, WS_PORT)
    log.info(f"[WS]   Servidor WebSocket en ws://{WS_HOST}:{WS_PORT}")

    # Servidor HTTP
    app = web.Application()
    app.router.add_post("/transcribir", http_transcribir)
    app.router.add_route("OPTIONS", "/transcribir", http_transcribir)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HTTP_HOST, HTTP_PORT)
    await site.start()
    log.info(f"[HTTP] Servidor HTTP en http://{HTTP_HOST}:{HTTP_PORT}/transcribir")

    log.info("Servidores listos. Esperando conexiones...")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
