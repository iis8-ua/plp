"""Perfil de aplicación asociado a un usuario de Django.

Django solo modela credenciales; el rol y la empresa a la que pertenece cada
usuario viven aquí.
"""

from django.conf import settings
from django.db import models

from .empresa import Empresa


class PerfilUsuario(models.Model):
    class Rol(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        TECNICO = 'tecnico', 'Técnico'
        COMERCIO = 'comercio', 'Comercio'

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='USUARIO_ID',
        related_name='perfil', verbose_name='usuario',
    )
    rol = models.CharField(
        'rol', max_length=10, choices=Rol, default=Rol.TECNICO, db_column='ROL'
    )
    empresa = models.ForeignKey(
        Empresa, on_delete=models.PROTECT, null=True, blank=True,
        db_column='EMPRESA_ID', related_name='usuarios', verbose_name='empresa',
    )
    force_password_change = models.BooleanField(
        'cambio de contraseña obligatorio', default=False,
        db_column='FORCE_PASSWORD_CHANGE',
    )

    class Meta:
        db_table = 'PERFILES_USUARIO'
        verbose_name = 'perfil de usuario'
        verbose_name_plural = 'perfiles de usuario'

    def __str__(self):
        return f'{self.usuario} ({self.rol})'
