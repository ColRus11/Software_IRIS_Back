from questions.entities.question_entity import Question


def obtener_todas():
    """Retorna todas las preguntas ordenadas por fecha."""
    return Question.objects.all()


def obtener_por_id(question_id):
    """Busca una pregunta por su ID. Retorna None si no existe."""
    return Question.objects.filter(id=question_id).first()


def filtrar(firebase_uid=None, session_name=None):
    """Filtra preguntas por firebase_uid y/o session_name.

    Args:
        firebase_uid: UID del usuario en Firebase.
        session_name: Nombre de la clase o sesión.

    Returns:
        QuerySet filtrado.
    """
    queryset = Question.objects.all()

    if firebase_uid:
        queryset = queryset.filter(firebase_uid=firebase_uid)
    if session_name:
        queryset = queryset.filter(session_name=session_name)

    return queryset


def crear(data):
    """Crea una nueva pregunta en la base de datos.

    Args:
        data: Diccionario con los campos de la pregunta.

    Returns:
        Instancia de Question creada.
    """
    return Question.objects.create(**data)


def actualizar(question_id, data):
    """Actualiza una pregunta existente.

    Args:
        question_id: ID de la pregunta a actualizar.
        data: Diccionario con los campos a actualizar.

    Returns:
        Instancia de Question actualizada o None.
    """
    question = obtener_por_id(question_id)
    if not question:
        return None

    for campo, valor in data.items():
        setattr(question, campo, valor)
    question.save()

    return question


def eliminar(question_id):
    """Elimina una pregunta por su ID.

    Args:
        question_id: ID de la pregunta a eliminar.

    Returns:
        True si se eliminó, False si no existía.
    """
    question = obtener_por_id(question_id)
    if not question:
        return False

    question.delete()
    return True


def marcar_hablada(question_id):
    """Marca una pregunta como reproducida con voz sintética.

    Args:
        question_id: ID de la pregunta.

    Returns:
        Instancia de Question actualizada o None.
    """
    question = obtener_por_id(question_id)
    if not question:
        return None

    question.was_spoken = True
    question.save()

    return question
