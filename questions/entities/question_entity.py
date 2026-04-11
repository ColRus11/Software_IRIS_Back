from django.db import models


class Question(models.Model):
    """Modelo para almacenar preguntas realizadas por estudiantes."""
    firebase_uid = models.CharField(
        max_length=128,
        help_text="UID del usuario en Firebase Authentication"
    )
    text = models.TextField(
        help_text="Texto de la pregunta"
    )
    session_name = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text="Nombre de la clase o sesión"
    )
    was_spoken = models.BooleanField(
        default=False,
        help_text="Indica si la pregunta fue reproducida con voz sintética"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'

    def __str__(self):
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {self.text[:50]}"
