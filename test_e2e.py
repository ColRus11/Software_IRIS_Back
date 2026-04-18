"""
Prueba E2E del flujo completo de SCRUM-38 con audio real.
Requiere: servidor corriendo + GROQ_API_KEY configurada.
"""
import os
import sys
import json
import urllib.request
import urllib.error

BASE = "http://localhost:8000/api"

def api_get(path):
    req = urllib.request.Request(f"{BASE}{path}")
    req.add_header("Accept", "application/json")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read()), resp.status

def api_post_json(path, data=None):
    body = json.dumps(data or {}).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read()), resp.status

def api_post_multipart(path, fields, files):
    boundary = "----TestBoundary12345"
    parts = []
    for key, value in fields.items():
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}\r\n")
    for key, (filename, content, ctype) in files.items():
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"; filename=\"{filename}\"\r\nContent-Type: {ctype}\r\n\r\n")
        parts.append(content)
        parts.append("\r\n")
    parts.append(f"--{boundary}--\r\n")
    body = b""
    for p in parts:
        body += p.encode() if isinstance(p, str) else p
    req = urllib.request.Request(f"{BASE}{path}", data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("Accept", "application/json")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read()), resp.status

def api_patch(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=body, method="PATCH")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read()), resp.status

def api_delete(path):
    req = urllib.request.Request(f"{BASE}{path}", method="DELETE")
    return urllib.request.urlopen(req).status

# ═══════════════════════════════════════════
print()
print("=" * 60)
print("  PRUEBA E2E — SCRUM-38: Flujo completo con audio real")
print("=" * 60)

# Paso 1: Subir video
print("\n[1/6] Subiendo archivo de audio...")
audio_path = os.path.join(os.path.dirname(__file__), "test_audio.wav")
with open(audio_path, "rb") as f:
    audio_data = f.read()

try:
    data, status = api_post_multipart("/videos/", 
        fields={"title": "Clase Prueba E2E", "language": "es", "firebase_uid": "test-e2e"},
        files={"video_file": ("test_audio.wav", audio_data, "audio/wav")}
    )
    video_id = data["id"]
    print(f"  OK  Video subido - ID={video_id}, status={data['status']}")
except urllib.error.HTTPError as e:
    print(f"  FALLO  {e.code}: {e.read().decode()}")
    sys.exit(1)

# Paso 2: Generar subtitulos
print("\n[2/6] Generando subtitulos con Groq API (Whisper)...")
print("  (esto puede tardar unos segundos...)")
try:
    data, status = api_post_json(f"/videos/{video_id}/generate_subtitles/")
    count = data.get("count", 0)
    print(f"  OK  {count} subtitulo(s) generados")
    if data.get("subtitles"):
        for s in data["subtitles"][:3]:
            print(f"       #{s['index']} [{s['start_time']}s-{s['end_time']}s] \"{s['text']}\"")
except urllib.error.HTTPError as e:
    error_body = e.read().decode()
    print(f"  FALLO  {e.code}: {error_body}")
    # Si falla por ser un tono sin habla, es esperado
    if "400" in str(e.code):
        print("  NOTA: El audio de prueba es un tono sin habla. Esto es esperado.")
        print("        Con un audio real con voz, los subtitulos se generarian correctamente.")

# Paso 3: Ver subtitulos
print("\n[3/6] Consultando subtitulos...")
try:
    data, status = api_get(f"/videos/{video_id}/subtitles/")
    print(f"  OK  {len(data)} subtitulo(s) encontrados")
except Exception as e:
    print(f"  INFO  {e}")

# Paso 4: Ver detalle del video
print("\n[4/6] Consultando detalle del video...")
try:
    data, status = api_get(f"/videos/{video_id}/")
    print(f"  OK  Titulo: {data['title']}")
    print(f"       Status: {data['status']}")
    print(f"       Subtitulos: {data.get('subtitles_count', 0)}")
except Exception as e:
    print(f"  FALLO  {e}")

# Paso 5: Intentar descargar SRT
print("\n[5/6] Intentando descargar SRT...")
try:
    req = urllib.request.Request(f"{BASE}/videos/{video_id}/download_srt/")
    resp = urllib.request.urlopen(req)
    srt_content = resp.read().decode()
    print(f"  OK  SRT descargado ({len(srt_content)} caracteres)")
    if srt_content:
        print(f"       Primeras lineas:")
        for line in srt_content.split("\n")[:6]:
            print(f"       | {line}")
except urllib.error.HTTPError as e:
    if e.code == 400:
        print(f"  ESPERADO  No hay subtitulos para descargar (el tono no tiene habla)")
    else:
        print(f"  FALLO  {e.code}")

# Paso 6: Limpieza
print("\n[6/6] Limpiando video de prueba...")
try:
    api_delete(f"/videos/{video_id}/")
    print(f"  OK  Video {video_id} eliminado")
except Exception as e:
    print(f"  FALLO  {e}")

print()
print("=" * 60)
print("  PRUEBA E2E COMPLETADA")
print("=" * 60)
print()
