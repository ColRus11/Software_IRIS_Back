from questions.entities.video_entity import Video, Subtitle


def crear_video(firebase_uid, title, video_file, language='es'):
    """Crea un nuevo registro de video en la base de datos.

    Args:
        firebase_uid: UID del docente en Firebase.
        title: Título del video.
        video_file: Archivo de video (InMemoryUploadedFile).
        language: Código de idioma ISO-639-1.

    Returns:
        Instancia de Video creada.
    """
    return Video.objects.create(
        firebase_uid=firebase_uid,
        title=title,
        video_file=video_file,
        language=language,
    )


def obtener_por_id(video_id):
    """Busca un video por ID. Retorna None si no existe."""
    return Video.objects.filter(id=video_id).first()


def listar_por_docente(firebase_uid):
    """Lista todos los videos de un docente."""
    return Video.objects.filter(firebase_uid=firebase_uid)


def listar_todos():
    """Lista todos los videos."""
    return Video.objects.all()


def actualizar_status(video_id, status, error_message=''):
    """Actualiza el estado de procesamiento de un video.

    Args:
        video_id: ID del video.
        status: Nuevo estado ('uploaded', 'processing', 'completed', 'published', 'error').
        error_message: Mensaje de error (solo si status='error').

    Returns:
        Instancia de Video actualizada o None.
    """
    video = obtener_por_id(video_id)
    if not video:
        return None

    video.status = status
    if error_message:
        video.error_message = error_message
    video.save()

    return video


def actualizar_duracion(video_id, duration):
    """Actualiza la duración del video."""
    video = obtener_por_id(video_id)
    if not video:
        return None

    video.duration = duration
    video.save()

    return video


def eliminar(video_id):
    """Elimina un video y todos sus subtítulos.

    Returns:
        True si se eliminó, False si no existía.
    """
    video = obtener_por_id(video_id)
    if not video:
        return False

    # Eliminar archivo físico
    if video.video_file:
        video.video_file.delete(save=False)

    video.delete()
    return True


# ───────── Subtítulos ─────────

def crear_subtitulos_bulk(video_id, segments):
    """Crea múltiples subtítulos de una vez (después de transcribir).

    Args:
        video_id: ID del video.
        segments: Lista de dicts con {index, start_time, end_time, text}.

    Returns:
        Lista de instancias Subtitle creadas.
    """
    video = obtener_por_id(video_id)
    if not video:
        return []

    # Eliminar subtítulos previos si existen (re-transcripción)
    Subtitle.objects.filter(video=video).delete()

    subtitles = [
        Subtitle(
            video=video,
            index=seg['index'],
            start_time=seg['start_time'],
            end_time=seg['end_time'],
            text=seg['text'],
        )
        for seg in segments
    ]

    return Subtitle.objects.bulk_create(subtitles)


def obtener_subtitulos(video_id):
    """Obtiene todos los subtítulos de un video, ordenados."""
    return Subtitle.objects.filter(video_id=video_id).order_by('index')


def obtener_subtitulo_por_id(subtitle_id):
    """Busca un subtítulo por ID."""
    return Subtitle.objects.filter(id=subtitle_id).first()


def actualizar_subtitulo(subtitle_id, text):
    """Actualiza el texto de un subtítulo y lo marca como editado.

    Args:
        subtitle_id: ID del subtítulo.
        text: Nuevo texto.

    Returns:
        Instancia de Subtitle actualizada o None.
    """
    subtitle = obtener_subtitulo_por_id(subtitle_id)
    if not subtitle:
        return None

    subtitle.text = text
    subtitle.is_edited = True
    subtitle.save()

    return subtitle
