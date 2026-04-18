"""
Script de pruebas funcionales para SCRUM-38.
Verifica todos los endpoints de la API de videos y subtítulos.

Ejecutar: python test_api.py
(con el servidor corriendo en otra terminal)
"""

import os
import sys
import json
import tempfile
import urllib.request
import urllib.error

BASE = "http://localhost:8000/api"
PASS = 0
FAIL = 0


def log(ok, test, detail=""):
    global PASS, FAIL
    status = "✅ PASS" if ok else "❌ FAIL"
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(f"  {status}  {test}")
    if detail and not ok:
        print(f"          → {detail}")


def api_get(path):
    req = urllib.request.Request(f"{BASE}{path}")
    req.add_header("Accept", "application/json")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read()), resp.status


def api_post_json(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read()), resp.status


def api_post_multipart(path, fields, files):
    """Envía multipart/form-data sin dependencias externas."""
    boundary = "----PythonTestBoundary12345"
    parts = []

    for key, value in fields.items():
        parts.append(f"--{boundary}\r\n")
        parts.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n')
        parts.append(f"{value}\r\n")

    for key, (filename, content, content_type) in files.items():
        parts.append(f"--{boundary}\r\n")
        parts.append(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"\r\n')
        parts.append(f"Content-Type: {content_type}\r\n\r\n")
        parts.append(content)
        parts.append("\r\n")

    parts.append(f"--{boundary}--\r\n")

    body = b""
    for p in parts:
        if isinstance(p, str):
            body += p.encode()
        else:
            body += p

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
    resp = urllib.request.urlopen(req)
    return resp.status


# ══════════════════════════════════════════
print("\n" + "═" * 60)
print("  PRUEBAS FUNCIONALES — SCRUM-38: Videos y Subtítulos")
print("═" * 60)

# ── Test 1: API Root ──
print("\n── API Root ──")
try:
    data, status = api_get("/../")
    log(status == 200, "GET / responde 200")
    log("videos" in str(data), "Root incluye endpoint de videos")
except Exception as e:
    log(False, f"GET / falló: {e}")

# ── Test 2: Questions (Sprint 1 - sigue funcionando?) ──
print("\n── Questions (regresión Sprint 1) ──")
try:
    data, status = api_get("/questions/")
    log(status == 200, "GET /api/questions/ responde 200")
    log("results" in data, "Respuesta paginada con 'results'")
except Exception as e:
    log(False, f"GET /api/questions/ falló: {e}")

try:
    q_data = {
        "firebase_uid": "test-pruebas-sprint2",
        "text": "¿Esto es una prueba automática del Sprint 2?",
        "session_name": "Prueba Automática"
    }
    data, status = api_post_json("/questions/", q_data)
    log(status == 201, "POST /api/questions/ crea pregunta (201)")
    q_id = data.get("id")
    log(q_id is not None, f"Pregunta creada con ID={q_id}")

    # Limpiar
    if q_id:
        api_delete(f"/questions/{q_id}/")
        log(True, f"DELETE /api/questions/{q_id}/ limpieza OK")
except Exception as e:
    log(False, f"POST /api/questions/ falló: {e}")

# ── Test 3: Videos - Listar vacío ──
print("\n── Videos — SCRUM-39: Subir Video ──")
try:
    data, status = api_get("/videos/")
    log(status == 200, "GET /api/videos/ responde 200")
    log(isinstance(data, list), "Respuesta es una lista")
except Exception as e:
    log(False, f"GET /api/videos/ falló: {e}")

# ── Test 4: Subir video ──
try:
    fake_audio = b"fake audio content for testing upload endpoint"
    fields = {
        "title": "Video de Prueba Automatica",
        "language": "es",
        "firebase_uid": "test-uid-sebastian",
    }
    files = {
        "video_file": ("test_audio.mp3", fake_audio, "audio/mpeg"),
    }
    data, status = api_post_multipart("/videos/", fields, files)
    log(status == 201, "POST /api/videos/ crea video (201)")
    video_id = data.get("id")
    log(video_id is not None, f"Video creado con ID={video_id}")
    log(data.get("status") == "uploaded", f"Status inicial = 'uploaded'")
    log(data.get("title") == "Video de Prueba Automatica", "Título guardado correctamente")
    log(data.get("firebase_uid") == "test-uid-sebastian", "firebase_uid guardado")
except urllib.error.HTTPError as e:
    error_body = e.read().decode()
    log(False, f"POST /api/videos/ falló: {e.code} — {error_body}")
    video_id = None
except Exception as e:
    log(False, f"POST /api/videos/ falló: {e}")
    video_id = None

# ── Test 5: Obtener detalle del video ──
if video_id:
    print("\n── Videos — Detalle y Listado ──")
    try:
        data, status = api_get(f"/videos/{video_id}/")
        log(status == 200, f"GET /api/videos/{video_id}/ responde 200")
        log("subtitles" in data, "Respuesta incluye campo 'subtitles'")
        log(data.get("subtitles_count") == 0, "subtitles_count = 0 (sin transcribir)")
    except Exception as e:
        log(False, f"GET /api/videos/{video_id}/ falló: {e}")

    # Listar filtrando por docente
    try:
        data, status = api_get("/videos/?firebase_uid=test-uid-sebastian")
        log(status == 200, "GET /api/videos/?firebase_uid=... responde 200")
        log(len(data) >= 1, f"Filtro por firebase_uid retorna {len(data)} video(s)")
    except Exception as e:
        log(False, f"GET filtrado falló: {e}")

# ── Test 6: Generar subtítulos (requiere GROQ_API_KEY) ──
    print("\n── Videos — SCRUM-41: Generar Subtítulos ──")
    groq_key = os.environ.get("GROQ_API_KEY", "")
    if groq_key:
        try:
            data, status = api_post_json(f"/videos/{video_id}/generate_subtitles/", {})
            log(status == 200, "POST generate_subtitles responde 200")
            log(data.get("count", 0) > 0, f"Generó {data.get('count', 0)} subtítulos")
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            log(False, f"generate_subtitles falló: {e.code} — {error_body}")
        except Exception as e:
            log(False, f"generate_subtitles falló: {e}")
    else:
        print("  ⚠️  SKIP  GROQ_API_KEY no configurada — no se puede probar transcripción real")
        print("          → Para probar: $env:GROQ_API_KEY='gsk_...' luego re-ejecutar")

# ── Test 7: Subtítulos endpoint ──
    print("\n── Videos — SCRUM-43: Subtítulos ──")
    try:
        data, status = api_get(f"/videos/{video_id}/subtitles/")
        log(status == 200, f"GET /api/videos/{video_id}/subtitles/ responde 200")
        log(isinstance(data, list), "Respuesta es una lista de subtítulos")
    except Exception as e:
        log(False, f"GET subtitles falló: {e}")

# ── Test 8: Descargar SRT ──
    print("\n── Videos — SCRUM-45: Publicar/Descargar ──")
    try:
        req = urllib.request.Request(f"{BASE}/videos/{video_id}/download_srt/")
        resp = urllib.request.urlopen(req)
        srt_status = resp.status
        log(srt_status == 200, f"GET download_srt responde 200")
    except urllib.error.HTTPError as e:
        if e.code == 400:
            log(True, "GET download_srt retorna 400 (no hay subtítulos aún — correcto)")
        else:
            log(False, f"GET download_srt falló: {e.code}")

    # Publicar (sin subtítulos debería fallar con 400)
    try:
        data, status = api_patch(f"/videos/{video_id}/publish/", {})
        log(False, "PATCH publish debería fallar sin subtítulos")
    except urllib.error.HTTPError as e:
        if e.code == 400:
            log(True, "PATCH publish retorna 400 (sin subtítulos — validación correcta)")
        else:
            log(False, f"PATCH publish falló inesperadamente: {e.code}")

# ── Test 9: Eliminar video ──
    print("\n── Limpieza ──")
    try:
        status = api_delete(f"/videos/{video_id}/")
        log(status == 204, f"DELETE /api/videos/{video_id}/ responde 204")
    except Exception as e:
        log(False, f"DELETE falló: {e}")

    # Verificar que fue eliminado
    try:
        api_get(f"/videos/{video_id}/")
        log(False, "El video debería no existir después de eliminar")
    except urllib.error.HTTPError as e:
        log(e.code == 404, "GET video eliminado retorna 404 (correcto)")

# ── Test 10: Errores y validaciones ──
print("\n── Validaciones de Error ──")
try:
    api_get("/videos/99999/")
    log(False, "GET video inexistente debería dar 404")
except urllib.error.HTTPError as e:
    log(e.code == 404, "GET /api/videos/99999/ retorna 404")

try:
    api_patch("/subtitles/99999/", {"text": "test"})
    log(False, "PATCH subtítulo inexistente debería dar 404")
except urllib.error.HTTPError as e:
    log(e.code == 404, "PATCH /api/subtitles/99999/ retorna 404")

# ══════════════════════════════════════════
print("\n" + "═" * 60)
print(f"  RESULTADOS: {PASS} pasaron ✅ | {FAIL} fallaron ❌")
print(f"  Total: {PASS + FAIL} pruebas")
print("═" * 60 + "\n")

if FAIL > 0:
    sys.exit(1)
