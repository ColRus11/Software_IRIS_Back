from rest_framework.exceptions import NotFound

from questions.repositories import question_repository


def listar_preguntas(firebase_uid=None, session=None):
    """Lista preguntas con filtros opcionales.

    Lógica de negocio: Orquesta el filtrado de preguntas
    delegando al repositorio.

    Args:
        firebase_uid: UID del usuario en Firebase (opcional).
        session: Nombre de la sesión/clase (opcional).

    Returns:
        QuerySet de preguntas filtradas.
    """
    if firebase_uid or session:
        return question_repository.filtrar(
            firebase_uid=firebase_uid,
            session_name=session,
        )
    return question_repository.obtener_todas()


def crear_pregunta(data):
    """Crea una nueva pregunta.

    Lógica de negocio: Valida los datos y delega la
    persistencia al repositorio.

    Args:
        data: Diccionario validado con los campos de la pregunta.

    Returns:
        Instancia de Question creada.
    """
    return question_repository.crear(data)


def obtener_pregunta(question_id):
    """Obtiene una pregunta por ID o lanza 404.

    Lógica de negocio: Verifica existencia y lanza
    excepción apropiada si no existe.

    Args:
        question_id: ID de la pregunta.

    Returns:
        Instancia de Question.

    Raises:
        NotFound: Si la pregunta no existe.
    """
    question = question_repository.obtener_por_id(question_id)
    if not question:
        raise NotFound("La pregunta no existe.")
    return question


def actualizar_pregunta(question_id, data):
    """Actualiza una pregunta existente.

    Lógica de negocio: Verifica existencia, valida y
    delega la actualización al repositorio.

    Args:
        question_id: ID de la pregunta a actualizar.
        data: Diccionario con los campos a actualizar.

    Returns:
        Instancia de Question actualizada.

    Raises:
        NotFound: Si la pregunta no existe.
    """
    question = question_repository.actualizar(question_id, data)
    if not question:
        raise NotFound("La pregunta no existe.")
    return question


def eliminar_pregunta(question_id):
    """Elimina una pregunta.

    Lógica de negocio: Verifica existencia antes de eliminar.

    Args:
        question_id: ID de la pregunta a eliminar.

    Raises:
        NotFound: Si la pregunta no existe.
    """
    eliminada = question_repository.eliminar(question_id)
    if not eliminada:
        raise NotFound("La pregunta no existe.")


def marcar_como_hablada(question_id):
    """Marca una pregunta como reproducida con voz sintética.

    Lógica de negocio: Verifica existencia y aplica la
    regla de negocio de marcar como hablada.

    Args:
        question_id: ID de la pregunta.

    Returns:
        Instancia de Question actualizada.

    Raises:
        NotFound: Si la pregunta no existe.
    """
    question = question_repository.marcar_hablada(question_id)
    if not question:
        raise NotFound("La pregunta no existe.")
    return question
