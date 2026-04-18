"""Servicio de transcripción automática usando Groq API (Whisper).

Responsabilidad única: Comunicación con la API de Groq para
convertir audio/video a texto con timestamps.

SCRUM-38 / SCRUM-41: Generar subtítulos.

Requisitos:
    pip install groq
    Variable de entorno: GROQ_API_KEY
"""

import os
import logging
import tempfile

from django.conf import settings

logger = logging.getLogger(__name__)


# Extensiones de audio/video soportadas por Groq
SUPPORTED_EXTENSIONS = {
    '.mp3', '.mp4', '.mpeg', '.mpga', '.m4a',
    '.wav', '.webm', '.ogg', '.flac',
}

# Tamaño máximo soportado por Groq: 25 MB
MAX_FILE_SIZE_MB = 25


def transcribir_archivo(file_path, language='es'):
    """Transcribe un archivo de audio/video usando Groq API.

    Envía el archivo a la API de Groq que ejecuta Whisper
    en la nube. No requiere GPU ni FFmpeg local.

    Args:
        file_path: Ruta absoluta al archivo de audio/video.
        language: Código ISO-639-1 del idioma (default: 'es').

    Returns:
        Lista de segmentos con formato:
        [
            {
                'index': 1,
                'start_time': 0.0,
                'end_time': 4.5,
                'text': 'Texto del segmento'
            },
            ...
        ]

    Raises:
        ValueError: Si el archivo no es válido.
        RuntimeError: Si la API falla.
    """
    from groq import Groq

    # Validar que la API key esté configurada
    api_key = getattr(settings, 'GROQ_API_KEY', None) or os.environ.get('GROQ_API_KEY')
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY no está configurada. "
            "Agrégala en settings.py o como variable de entorno."
        )

    # Validar archivo
    if not os.path.exists(file_path):
        raise ValueError(f"El archivo no existe: {file_path}")

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(
            f"El archivo es demasiado grande ({file_size_mb:.1f} MB). "
            f"Máximo permitido: {MAX_FILE_SIZE_MB} MB."
        )

    # Inicializar cliente Groq
    client = Groq(api_key=api_key)

    logger.info(f"Iniciando transcripción: {file_path} ({file_size_mb:.1f} MB, idioma: {language})")

    try:
        with open(file_path, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(file_path), audio_file.read()),
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
                timestamp_granularities=["segment"],
                language=language,
            )
    except Exception as e:
        logger.error(f"Error en la API de Groq: {e}")
        raise RuntimeError(f"Error al transcribir con Groq: {str(e)}")

    # Parsear segmentos
    segments = []
    if hasattr(transcription, 'segments') and transcription.segments:
        for i, seg in enumerate(transcription.segments, start=1):
            # Groq puede retornar segmentos como objetos o dicts
            if isinstance(seg, dict):
                start = seg.get('start', 0)
                end = seg.get('end', 0)
                text = seg.get('text', '')
            else:
                start = seg.start
                end = seg.end
                text = seg.text

            segments.append({
                'index': i,
                'start_time': round(start, 2),
                'end_time': round(end, 2),
                'text': text.strip(),
            })

    logger.info(f"Transcripción completada: {len(segments)} segmentos generados")

    return segments


def generar_srt(segments):
    """Convierte una lista de segmentos a formato SRT.

    Args:
        segments: Lista de dicts con {index, start_time, end_time, text}.

    Returns:
        String con el contenido del archivo .srt.
    """
    lines = []

    for seg in segments:
        start = _seconds_to_srt_time(seg['start_time'])
        end = _seconds_to_srt_time(seg['end_time'])

        lines.append(str(seg['index']))
        lines.append(f"{start} --> {end}")
        lines.append(seg['text'])
        lines.append('')  # Línea en blanco entre segmentos

    return '\n'.join(lines)


def _seconds_to_srt_time(seconds):
    """Convierte segundos a formato SRT (HH:MM:SS,mmm).

    Args:
        seconds: Tiempo en segundos (float).

    Returns:
        String en formato '00:01:23,456'.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
