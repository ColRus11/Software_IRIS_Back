"""
IRIS - Backend WebSocket + Whisper
------------------------------------
Recibe fragmentos de audio desde el front via WebSocket,
los transcribe con Whisper y devuelve el texto al front.

Uso:
    python3 main.py

Requisitos:
    pip install -r requirements.txt
"""

import asyncio
import websockets
import whisper
import tempfile
import os
import logging

# ─── Configuración ────────────────────────────────────────
HOST    = "0.0.0.0"   # Acepta conexiones de cualquier IP
PORT    = 8765        # Debe coincidir con WS_URL en el front
MODEL   = "base"      # tiny | base | small | medium | large
LANG    = "es"        # Idioma esperado del audio

# ─── Logging ──────────────────────────────────────────────
logging.basicConfig(
    level  = logging.INFO,
    format = "[%(asctime)s] %(levelname)s - %(message)s",
    datefmt= "%H:%M:%S"
)
log = logging.getLogger("IRIS")

# ─── Carga del modelo (una sola vez al iniciar) ───────────
log.info(f"Cargando modelo Whisper '{MODEL}'...")
modelo = whisper.load_model(MODEL)
log.info("Modelo listo.")

# ─── Handler por cliente ──────────────────────────────────
async def handler(websocket):
    cliente = websocket.remote_address
    log.info(f"Cliente conectado: {cliente}")

    try:
        async for mensaje in websocket:
            # El front envía fragmentos de audio como bytes
            if not isinstance(mensaje, bytes) or len(mensaje) == 0:
                continue

            log.info(f"Fragmento recibido: {len(mensaje)} bytes")

            # Guarda el fragmento en un archivo temporal
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(mensaje)
                tmp_path = tmp.name

            try:
                # Transcribe con Whisper
                resultado = modelo.transcribe(
                    tmp_path,
                    language        = LANG,
                    fp16            = False,  # False para compatibilidad en CPU
                    condition_on_previous_text = True
                )
                texto = resultado["text"].strip()

                if texto:
                    log.info(f"Transcripción: {texto}")
                    await websocket.send(texto)
                else:
                    log.info("Fragmento sin texto detectable")

            except Exception as e:
                log.error(f"Error en transcripción: {e}")

            finally:
                # Elimina el archivo temporal
                os.unlink(tmp_path)

    except websockets.exceptions.ConnectionClosedOK:
        log.info(f"Cliente desconectado: {cliente}")
    except websockets.exceptions.ConnectionClosedError as e:
        log.warning(f"Conexión cerrada con error: {e}")
    except Exception as e:
        log.error(f"Error inesperado: {e}")

# ─── Inicio del servidor ──────────────────────────────────
async def main():
    log.info(f"Servidor WebSocket iniciando en ws://{HOST}:{PORT}")
    async with websockets.serve(handler, HOST, PORT):
        log.info("Servidor listo. Esperando conexiones...")
        await asyncio.Future()  # Corre indefinidamente

if __name__ == "__main__":
    asyncio.run(main())
