from django.db import models

class TranscriptionSession(models.Model):
    """Sesión de transcripción en tiempo real."""
    teacher_uid  = models.CharField(max_length=128, help_text="firebase_uid del docente")
    session_name = models.CharField(max_length=200, blank=True, default='')
    transcript   = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sesión de Transcripción'

    def __str__(self):
        return f"{self.session_name or 'Sin nombre'} — {self.created_at:%Y-%m-%d %H:%M}"
