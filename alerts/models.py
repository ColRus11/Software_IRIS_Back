from django.db import models

class EmergencyAlert(models.Model):
    """Alerta de emergencia del campus."""
    SEVERITY_CHOICES = [
        ('info',      'Información'),
        ('warning',   'Advertencia'),
        ('emergency', 'Emergencia'),
    ]
    title      = models.CharField(max_length=200)
    message    = models.TextField()
    severity   = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='info')
    is_active  = models.BooleanField(default=True)
    created_by = models.CharField(max_length=128, blank=True, help_text="firebase_uid del admin")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Alerta de Emergencia'

    def __str__(self):
        return f"[{self.severity.upper()}] {self.title}"
