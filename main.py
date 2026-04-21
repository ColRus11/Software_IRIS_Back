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

    fragmentos = []

    try:
        async for mensaje in websocket:
            # El front envía "FIN" como señal de fin de grabación
            if isinstance(mensaje, str) and mensaje == "FIN":
                log.info("Señal FIN recibida, transcribiendo...")
                break

            if isinstance(mensaje, bytes) and len(mensaje) > 0:
                fragmentos.append(mensaje)
                total = sum(len(f) for f in fragmentos)
                log.info(f"Fragmento #{len(fragmentos)}: {len(mensaje)} bytes (total: {total} bytes)")

    except websockets.exceptions.ConnectionClosedError as e:
        log.warning(f"Conexión cerrada con error: {e}")

    # Transcribe y responde antes de cerrar
    if fragmentos:
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
                log.info(f"Transcripción: {texto}")
                await websocket.send(texto)
            else:
                log.info("Sin texto detectado.")
                await websocket.send("(sin texto detectado)")
        except Exception as e:
            log.error(f"Error en transcripción: {e}")
        finally:
            os.unlink(tmp_path)
    else:
        log.info("Sin fragmentos de audio.")

# ─── Inicio del servidor ──────────────────────────────────
async def main():
    log.info(f"Servidor WebSocket iniciando en ws://{HOST}:{PORT}")
    async with websockets.serve(handler, HOST, PORT):
        log.info("Servidor listo. Esperando conexiones...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
