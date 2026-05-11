from django.db import models
from django.contrib.auth.models import User


class EmergencyAlert(models.Model):
    SEVERITY_CHOICES = [
        ('info',      'Información'),
        ('warning',   'Advertencia'),
        ('emergency', 'Emergencia'),
    ]
    title      = models.CharField(max_length=200)
    message    = models.TextField()
    severity   = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='info')
    is_active  = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Alerta de Emergencia'

    def __str__(self):
        return f"[{self.severity.upper()}] {self.title}"
