"""
IRIS - Backend WebSocket + Whisper
------------------------------------
Recibe fragmentos de audio desde el front via WebSocket,
acumula los fragmentos y transcribe con Whisper al finalizar.

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

# ─── Configuración ────────────────────────────────────────
HOST    = "0.0.0.0"
PORT    = 8765
MODEL   = "base"
LANG    = "es"

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

# ─── Handler por cliente ──────────────────────────────────
async def handler(websocket):
    cliente = websocket.remote_address
    log.info(f"Cliente conectado: {cliente}")

    fragmentos = []  # Acumula todos los fragmentos del cliente

    try:
        async for mensaje in websocket:
            if not isinstance(mensaje, bytes) or len(mensaje) == 0:
                continue

            fragmentos.append(mensaje)
            total = sum(len(f) for f in fragmentos)
            log.info(f"Fragmento #{len(fragmentos)} recibido: {len(mensaje)} bytes (total: {total} bytes)")

            # Avisa al front que se recibió el fragmento
            await websocket.send("...")

    except websockets.exceptions.ConnectionClosedOK:
        log.info(f"Cliente desconectado: {cliente}")
    except websockets.exceptions.ConnectionClosedError as e:
        log.warning(f"Conexión cerrada con error: {e}")
    except Exception as e:
        log.error(f"Error inesperado: {e}")

    # ── Al cerrar la conexión, transcribe el audio completo ──
    if not fragmentos:
        log.info("Sin audio para transcribir.")
        return

    log.info(f"Transcribiendo {len(fragmentos)} fragmentos...")

    audio_completo = b"".join(fragmentos)

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(audio_completo)
        tmp_path = tmp.name

    try:
        resultado = modelo.transcribe(
            tmp_path,
            language                   = LANG,
            fp16                       = False,
            condition_on_previous_text = True
        )
        texto = resultado["text"].strip()

        if texto:
            log.info(f"Transcripción completa: {texto}")
            # Intenta enviar el texto final (si el cliente aún escucha)
            try:
                await websocket.send(texto)
            except Exception:
                log.info("Cliente ya cerrado, transcripción guardada solo en log.")
        else:
            log.info("Sin texto detectado en el audio.")

    except Exception as e:
        log.error(f"Error en transcripción: {e}")

    finally:
        os.unlink(tmp_path)

# ─── Inicio del servidor ──────────────────────────────────
async def main():
    log.info(f"Servidor WebSocket iniciando en ws://{HOST}:{PORT}")
    async with websockets.serve(handler, HOST, PORT):
        log.info("Servidor listo. Esperando conexiones...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
