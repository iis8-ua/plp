"""Empresas que cobran a través de la pasarela."""

import uuid

from django.db import models


class Empresa(models.Model):
    id = models.UUIDField(
        'identificador', primary_key=True, default=uuid.uuid4, editable=False,
        db_column='ID',
    )
    nombre = models.CharField('nombre', max_length=100, db_column='NOMBRE')
    fecha_registro = models.DateTimeField(
        'fecha de registro', auto_now_add=True, db_column='FECHA_REGISTRO'
    )

    class Meta:
        db_table = 'EMPRESAS'
        ordering = ['nombre']
        verbose_name = 'empresa'
        verbose_name_plural = 'empresas'

    def __str__(self):
        return self.nombre
