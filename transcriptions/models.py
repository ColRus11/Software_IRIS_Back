from django.db import models
from django.contrib.auth.models import User


class TranscriptionSession(models.Model):
    teacher      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transcriptions')
    session_name = models.CharField(max_length=200, blank=True, default='')
    transcript   = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sesión de Transcripción'

    def __str__(self):
        return f"{self.session_name or 'Sin nombre'} — {self.created_at:%Y-%m-%d %H:%M}"


class GroupTranscriptionSession(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_sessions')
    session_name = models.CharField(max_length=200, blank=True, default='')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sesión de Transcripción Grupal'

    def __str__(self):
        return f"Grupo: {self.session_name or 'Sin nombre'} — {self.created_at:%Y-%m-%d %H:%M}"


class GroupTranscriptionEntry(models.Model):
    session       = models.ForeignKey(GroupTranscriptionSession, on_delete=models.CASCADE, related_name='entries')
    speaker_index = models.PositiveSmallIntegerField(default=1)
    speaker_label = models.CharField(max_length=50, default='Speaker 1')
    text          = models.TextField()
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.speaker_label}: {self.text[:40]}"
