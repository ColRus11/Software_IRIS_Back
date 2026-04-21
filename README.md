# IRIS - Backend

Servidor WebSocket que recibe fragmentos de audio desde el front,
los transcribe con Whisper y devuelve el texto en tiempo real.

## Requisitos

- Python 3.8+
- pip

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
python3 main.py
```

El servidor queda corriendo en `ws://localhost:8765`.

## Modelos disponibles

Edita la variable `MODEL` en `main.py` según tus necesidades:

| Modelo  | Velocidad | Precisión | RAM aprox |
|---------|-----------|-----------|-----------|
| tiny    | Muy rápido | Básica   | ~1 GB     |
| base    | Rápido     | Buena    | ~1 GB     |
| small   | Medio      | Mejor    | ~2 GB     |
| medium  | Lento      | Alta     | ~5 GB     |
| large   | Muy lento  | Máxima   | ~10 GB    |

Para pruebas locales se recomienda `base`. Para producción, `small` o `medium`.

## Variables de configuración

En `main.py`:

```python
HOST  = "0.0.0.0"  # Cambia a "localhost" si solo quieres acceso local
PORT  = 8765       # Debe coincidir con WS_URL en el front
MODEL = "base"     # Ver tabla de modelos
LANG  = "es"       # Idioma del audio
```
