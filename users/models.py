from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Student', 'Estudiante'),
        ('Teacher', 'Docente'),
        ('Admin',   'Admin'),
    ]
    user         = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    display_name = models.CharField(max_length=200, blank=True)
    role         = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Student')
    university   = models.CharField(max_length=200, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_name']
        verbose_name = 'Perfil de Usuario'

    def __str__(self):
        return f"{self.display_name} ({self.role})"
