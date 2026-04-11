from django.db import models


class Video(models.Model):
    """Video subido por un docente para generar subtítulos automáticos.

    SCRUM-38 / SCRUM-39: Subir video.
    """

    STATUS_CHOICES = [
        ('uploaded', 'Subido'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('published', 'Publicado'),
        ('error', 'Error'),
    ]

    firebase_uid = models.CharField(
        max_length=128,
        help_text="UID del docente en Firebase Authentication"
    )
    title = models.CharField(
        max_length=300,
        help_text="Título del video"
    )
    video_file = models.FileField(
        upload_to='videos/%Y/%m/',
        help_text="Archivo de video subido"
    )
    duration = models.FloatField(
        null=True,
        blank=True,
        help_text="Duración del video en segundos"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='uploaded',
        help_text="Estado actual del procesamiento"
    )
    language = models.CharField(
        max_length=10,
        default='es',
        help_text="Idioma del audio (código ISO-639-1)"
    )
    error_message = models.TextField(
        blank=True,
        default='',
        help_text="Mensaje de error si la transcripción falló"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title}"


class Subtitle(models.Model):
    """Segmento individual de subtítulo generado automáticamente.

    SCRUM-38 / SCRUM-41: Generar subtítulos.
    """

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='subtitles',
        help_text="Video al que pertenece este subtítulo"
    )
    index = models.PositiveIntegerField(
        help_text="Número de orden del segmento (1, 2, 3...)"
    )
    start_time = models.FloatField(
        help_text="Tiempo de inicio en segundos"
    )
    end_time = models.FloatField(
        help_text="Tiempo de fin en segundos"
    )
    text = models.TextField(
        help_text="Texto del subtítulo"
    )
    is_edited = models.BooleanField(
        default=False,
        help_text="Indica si fue editado manualmente por el docente"
    )

    class Meta:
        ordering = ['video', 'index']
        verbose_name = 'Subtítulo'
        verbose_name_plural = 'Subtítulos'
        unique_together = ['video', 'index']

    def __str__(self):
        return f"#{self.index} [{self.start_time:.1f}s-{self.end_time:.1f}s] {self.text[:40]}"
