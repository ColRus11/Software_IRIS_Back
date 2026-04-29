from django.db import models

class UserProfile(models.Model):
    """Perfil de usuario — réplica de User.cs del repo MAUI del compañero."""
    firebase_uid = models.CharField(max_length=128, unique=True)
    display_name = models.CharField(max_length=200, blank=True)
    email        = models.EmailField(blank=True)
    role         = models.CharField(
        max_length=20,
        choices=[('Student','Estudiante'), ('Teacher','Docente'), ('Admin','Admin')],
        default='Student'
    )
    university   = models.CharField(max_length=200, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_name']
        verbose_name = 'Perfil de Usuario'

    def __str__(self):
        return f"{self.display_name} ({self.role})"
