# 📖 Diccionario de Variables — IRIS Backend

Documento de referencia para todo el equipo. Contiene las variables, campos, endpoints, y constantes usadas en el backend de IRIS.

> **Última actualización:** Sprint 2 (SCRUM-38)  
> **Tecnología:** Django 6.0 + Django REST Framework 3.17 + Groq API  
> **Base de datos:** SQLite (desarrollo) 

---

## 📐 Arquitectura de Capas (SOLID)

```
questions/
├── entities/          → Definición de modelos ORM (estructura de datos)
│   ├── question_entity.py
│   └── video_entity.py       ← SCRUM-38
├── schemas/           → Serializers / DTOs (forma de datos en la API)
│   ├── question_schema.py
│   └── video_schema.py       ← SCRUM-38
├── repositories/      → Acceso a datos (CRUD puro contra la BD)
│   ├── question_repository.py
│   └── video_repository.py   ← SCRUM-38
├── services/          → Lógica de negocio (validaciones, reglas)
│   ├── question_service.py
│   ├── video_service.py       ← SCRUM-38
│   └── transcription_service.py  ← SCRUM-41
├── views/             → Manejo HTTP (request → service → response)
│   ├── question_view.py
│   └── video_view.py         ← SCRUM-38
├── urls.py            → Definición de rutas
├── admin.py           → Panel de administración Django
├── models.py          → Proxy (re-importa desde entities/)
└── migrations/        → Migraciones de base de datos
```

---

## 🗄️ Entidad: `Question`

**Archivo:** `questions/entities/question_entity.py`  
**Tabla en BD:** `questions_question`

| Campo | Tipo Django | Tipo BD | Restricciones | Descripción |
|-------|-------------|---------|---------------|-------------|
| `id` | `AutoField` (implícito) | `INTEGER` | PK, auto-increment | Identificador único de la pregunta |
| `firebase_uid` | `CharField(max_length=128)` | `VARCHAR(128)` | Requerido | UID del usuario en Firebase Authentication |
| `text` | `TextField` | `TEXT` | Requerido | Texto completo de la pregunta del estudiante |
| `session_name` | `CharField(max_length=200)` | `VARCHAR(200)` | Opcional, default=`''` | Nombre de la clase o sesión académica |
| `was_spoken` | `BooleanField` | `BOOLEAN` | Default=`False` | Indica si la pregunta fue reproducida con voz sintética (TTS) |
| `created_at` | `DateTimeField(auto_now_add=True)` | `DATETIME` | Auto, read-only | Fecha y hora de creación |

**Meta:**
- `ordering`: `['-created_at']` (más recientes primero)
- `verbose_name`: `'Pregunta'`
- `verbose_name_plural`: `'Preguntas'`

---

## 🗄️ Entidad: `Video` (SCRUM-38)

**Archivo:** `questions/entities/video_entity.py`  
**Tabla en BD:** `questions_video`

| Campo | Tipo Django | Tipo BD | Restricciones | Descripción |
|-------|-------------|---------|---------------|-------------|
| `id` | `BigAutoField` | `INTEGER` | PK, auto-increment | Identificador único del video |
| `firebase_uid` | `CharField(max_length=128)` | `VARCHAR(128)` | Requerido | UID del docente en Firebase |
| `title` | `CharField(max_length=300)` | `VARCHAR(300)` | Requerido | Título del video |
| `video_file` | `FileField(upload_to='videos/%Y/%m/')` | `VARCHAR(100)` | Requerido | Ruta del archivo de video |
| `duration` | `FloatField` | `REAL` | Nullable | Duración en segundos |
| `status` | `CharField(max_length=20)` | `VARCHAR(20)` | Default=`'uploaded'` | Estado del procesamiento |
| `language` | `CharField(max_length=10)` | `VARCHAR(10)` | Default=`'es'` | Idioma del audio (ISO-639-1) |
| `error_message` | `TextField` | `TEXT` | Opcional, default=`''` | Mensaje de error si falló |
| `created_at` | `DateTimeField(auto_now_add=True)` | `DATETIME` | Auto, read-only | Fecha de subida |
| `updated_at` | `DateTimeField(auto_now=True)` | `DATETIME` | Auto | Última actualización |

**Status choices:**
- `uploaded` → Subido
- `processing` → Procesando
- `completed` → Subtítulos listos
- `published` → Publicado
- `error` → Error

---

## 🗄️ Entidad: `Subtitle` (SCRUM-41)

**Archivo:** `questions/entities/video_entity.py`  
**Tabla en BD:** `questions_subtitle`

| Campo | Tipo Django | Tipo BD | Restricciones | Descripción |
|-------|-------------|---------|---------------|-------------|
| `id` | `BigAutoField` | `INTEGER` | PK, auto-increment | Identificador único |
| `video` | `ForeignKey(Video)` | `INTEGER` | FK, CASCADE | Video al que pertenece |
| `index` | `PositiveIntegerField` | `INTEGER` | Requerido | Número de orden (1, 2, 3...) |
| `start_time` | `FloatField` | `REAL` | Requerido | Tiempo de inicio en segundos |
| `end_time` | `FloatField` | `REAL` | Requerido | Tiempo de fin en segundos |
| `text` | `TextField` | `TEXT` | Requerido | Texto del subtítulo |
| `is_edited` | `BooleanField` | `BOOLEAN` | Default=`False` | Si fue editado manualmente |

**Meta:**
- `unique_together`: `['video', 'index']`
- `ordering`: `['video', 'index']`

---

## 📡 API Endpoints

**Base URL:** `http://localhost:8000/api/`

### Preguntas (`/api/questions/`)

| Método | Endpoint | Descripción | Body / Params |
|--------|----------|-------------|---------------|
| `GET` | `/api/questions/` | Listar preguntas | Query params: `firebase_uid`, `session` |
| `POST` | `/api/questions/` | Crear pregunta | Body JSON |
| `GET` | `/api/questions/{id}/` | Detalle de pregunta | — |
| `PUT` | `/api/questions/{id}/` | Actualizar pregunta completa | Body JSON completo |
| `PATCH` | `/api/questions/{id}/` | Actualizar parcialmente | Body JSON parcial |
| `DELETE` | `/api/questions/{id}/` | Eliminar pregunta | — |
| `PATCH` | `/api/questions/{id}/mark_spoken/` | Marcar como reproducida | — |

### Videos (`/api/videos/`) — SCRUM-38

| Método | Endpoint | Subtarea | Descripción | Body / Params |
|--------|----------|----------|-------------|---------------|
| `POST` | `/api/videos/` | SCRUM-39 | Subir video | FormData: `title`, `video_file`, `language` |
| `GET` | `/api/videos/` | SCRUM-45 | Listar videos | Query params: `firebase_uid` |
| `GET` | `/api/videos/{id}/` | SCRUM-45 | Detalle con subtítulos | — |
| `DELETE` | `/api/videos/{id}/` | — | Eliminar video | — |
| `POST` | `/api/videos/{id}/generate_subtitles/` | SCRUM-41 | Generar subtítulos | — |
| `GET` | `/api/videos/{id}/subtitles/` | SCRUM-43 | Listar subtítulos | — |
| `GET` | `/api/videos/{id}/download_srt/` | SCRUM-45 | Descargar archivo .srt | — |
| `PATCH` | `/api/videos/{id}/publish/` | SCRUM-45 | Publicar video | — |

### Subtítulos (`/api/subtitles/`) — SCRUM-43

| Método | Endpoint | Descripción | Body |
|--------|----------|-------------|------|
| `PATCH` | `/api/subtitles/{id}/` | Editar texto de un subtítulo | `{ "text": "nuevo texto" }` |

### Raíz (`/`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Info de la API (nombre, versión, endpoints) |
| `GET` | `/admin/` | Panel de administración Django |

---

## 📨 Schemas (DTOs)

### Request Body — Subir Video (`POST /api/videos/`)

**Content-Type:** `multipart/form-data`

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `title` | `string` | ✅ | Título del video (max 300 chars) |
| `video_file` | `file` | ✅ | Archivo de video (max 25 MB) |
| `language` | `string` | ❌ | Idioma del audio (default: `es`) |

**Formatos soportados:** `.mp4`, `.webm`, `.mov`, `.avi`, `.mkv`, `.m4a`, `.mp3`, `.wav`, `.ogg`

### Response — Video

```json
{
    "id": 1,
    "firebase_uid": "abc123xyz",
    "title": "Clase de Cálculo II - Integrales",
    "video_file": "/media/videos/2026/04/clase_calculo.mp4",
    "duration": null,
    "status": "completed",
    "language": "es",
    "error_message": "",
    "subtitles_count": 15,
    "subtitles": [
        {
            "id": 1,
            "index": 1,
            "start_time": 0.0,
            "end_time": 4.5,
            "text": "Buenos días estudiantes",
            "is_edited": false
        }
    ],
    "created_at": "2026-04-11T07:50:00-05:00",
    "updated_at": "2026-04-11T07:51:00-05:00"
}
```

---

## 📋 Query Parameters

| Parámetro | Endpoint | Tipo | Descripción |
|-----------|----------|------|-------------|
| `firebase_uid` | `GET /api/questions/` | `string` | Filtrar preguntas por UID |
| `session` | `GET /api/questions/` | `string` | Filtrar por nombre de sesión |
| `firebase_uid` | `GET /api/videos/` | `string` | Filtrar videos por UID del docente |
| `page` | `GET /api/questions/` | `integer` | Paginación (20 por página) |

---

## ⚙️ Variables de Configuración (`settings.py`)

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `SECRET_KEY` | `django-insecure-...` | ⚠️ Cambiar en producción |
| `DEBUG` | `True` | Modo desarrollo |
| `ALLOWED_HOSTS` | `['*']` | Hosts permitidos |
| `CORS_ALLOW_ALL_ORIGINS` | `True` | ⚠️ Solo para desarrollo |
| `LANGUAGE_CODE` | `es-co` | Idioma: Español Colombia |
| `TIME_ZONE` | `America/Bogota` | Zona horaria |
| `PAGE_SIZE` | `20` | Items por página |
| `DEFAULT_PERMISSION_CLASSES` | `AllowAny` | Sin autenticación en API |
| `MEDIA_URL` | `/media/` | URL base para archivos media |
| `MEDIA_ROOT` | `BASE_DIR / 'media'` | Carpeta física de uploads |
| `GROQ_API_KEY` | `env: GROQ_API_KEY` | API key de Groq (transcripción) |
| `FILE_UPLOAD_MAX_MEMORY_SIZE` | `26214400` (25 MB) | Tamaño máximo de upload |

---

## 🔴 Códigos de Error HTTP

| Código | Significado | Cuándo se usa |
|--------|-------------|---------------|
| `200` | OK | Respuesta exitosa (GET, PUT, PATCH) |
| `201` | Created | Video/Pregunta creada exitosamente (POST) |
| `204` | No Content | Eliminado exitosamente (DELETE) |
| `400` | Bad Request | Datos inválidos, archivo muy grande, formato no soportado |
| `404` | Not Found | Video/Pregunta/Subtítulo no existe |
| `500` | Internal Server Error | Error del servidor |

---

## 📂 Repositorio — Funciones (`question_repository.py`)

| Función | Parámetros | Retorno | Descripción |
|---------|------------|---------|-------------|
| `obtener_todas()` | — | `QuerySet` | Todas las preguntas |
| `obtener_por_id(question_id)` | `int` | `Question \| None` | Buscar por ID |
| `filtrar(firebase_uid, session_name)` | `str, str` | `QuerySet` | Filtrar por usuario/sesión |
| `crear(data)` | `dict` | `Question` | Crear pregunta |
| `actualizar(question_id, data)` | `int, dict` | `Question \| None` | Actualizar |
| `eliminar(question_id)` | `int` | `bool` | Eliminar |
| `marcar_hablada(question_id)` | `int` | `Question \| None` | Marcar como hablada |

## 📂 Repositorio — Funciones (`video_repository.py`) — SCRUM-38

| Función | Parámetros | Retorno | Descripción |
|---------|------------|---------|-------------|
| `crear_video(firebase_uid, title, video_file, language)` | `str, str, File, str` | `Video` | Crear video |
| `obtener_por_id(video_id)` | `int` | `Video \| None` | Buscar video |
| `listar_por_docente(firebase_uid)` | `str` | `QuerySet` | Videos del docente |
| `listar_todos()` | — | `QuerySet` | Todos los videos |
| `actualizar_status(video_id, status, error_message)` | `int, str, str` | `Video \| None` | Cambiar estado |
| `actualizar_duracion(video_id, duration)` | `int, float` | `Video \| None` | Actualizar duración |
| `eliminar(video_id)` | `int` | `bool` | Eliminar video + archivo |
| `crear_subtitulos_bulk(video_id, segments)` | `int, list[dict]` | `list[Subtitle]` | Guardar subtítulos en masa |
| `obtener_subtitulos(video_id)` | `int` | `QuerySet` | Listar subtítulos |
| `obtener_subtitulo_por_id(subtitle_id)` | `int` | `Subtitle \| None` | Buscar subtítulo |
| `actualizar_subtitulo(subtitle_id, text)` | `int, str` | `Subtitle \| None` | Editar texto |

---

## 🔧 Servicio — Funciones (`question_service.py`)

| Función | Parámetros | Retorno | Excepciones |
|---------|------------|---------|-------------|
| `listar_preguntas(firebase_uid, session)` | `str?, str?` | `QuerySet` | — |
| `crear_pregunta(data)` | `dict` | `Question` | — |
| `obtener_pregunta(question_id)` | `int` | `Question` | `NotFound` |
| `actualizar_pregunta(question_id, data)` | `int, dict` | `Question` | `NotFound` |
| `eliminar_pregunta(question_id)` | `int` | — | `NotFound` |
| `marcar_como_hablada(question_id)` | `int` | `Question` | `NotFound` |

## 🔧 Servicio — Funciones (`video_service.py`) — SCRUM-38

| Función | Parámetros | Retorno | Excepciones |
|---------|------------|---------|-------------|
| `subir_video(video_file, title, firebase_uid, language)` | `File, str, str, str` | `Video` | `ValidationError` |
| `generar_subtitulos(video_id)` | `int` | `list[Subtitle]` | `NotFound`, `ValidationError` |
| `editar_subtitulo(subtitle_id, nuevo_texto)` | `int, str` | `Subtitle` | `NotFound`, `ValidationError` |
| `obtener_video(video_id)` | `int` | `Video` | `NotFound` |
| `listar_videos(firebase_uid)` | `str?` | `QuerySet` | — |
| `eliminar_video(video_id)` | `int` | — | `NotFound` |
| `exportar_srt(video_id)` | `int` | `(filename, srt_content)` | `NotFound`, `ValidationError` |
| `publicar_video(video_id)` | `int` | `Video` | `NotFound`, `ValidationError` |

## 🔧 Servicio — Funciones (`transcription_service.py`) — SCRUM-41

| Función | Parámetros | Retorno | Excepciones |
|---------|------------|---------|-------------|
| `transcribir_archivo(file_path, language)` | `str, str` | `list[dict]` | `ValueError`, `RuntimeError` |
| `generar_srt(segments)` | `list[dict]` | `str` | — |

**Motor de transcripción:** Groq API + Whisper-large-v3-turbo (nube, no requiere GPU)

---

## 📦 Dependencias (`requirements.txt`)

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `django` | `>=6.0,<7.0` | Framework web principal |
| `djangorestframework` | `>=3.17` | API REST |
| `django-cors-headers` | `>=4.9` | Manejo de CORS |
| `firebase-admin` | `>=7.3` | Integración con Firebase |
| `groq` | `>=0.12` | Transcripción de audio (Whisper en la nube) |
