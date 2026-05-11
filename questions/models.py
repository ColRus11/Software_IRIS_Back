from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    text         = models.TextField()
    session_name = models.CharField(max_length=200, blank=True, default='')
    was_spoken   = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'

    def __str__(self):
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {self.text[:50]}"
