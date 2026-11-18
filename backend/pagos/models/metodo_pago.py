"""Catálogo de métodos de pago (tarjeta, transferencia, Bizum...)."""

import uuid

from django.db import models


class MetodoPago(models.Model):
    id = models.UUIDField(
        'identificador', primary_key=True, default=uuid.uuid4, editable=False,
        db_column='ID',
    )
    nombre = models.CharField('nombre', max_length=30, db_column='NOMBRE')

    class Meta:
        db_table = 'METODOS_PAGO'
        ordering = ['nombre']
        verbose_name = 'método de pago'
        verbose_name_plural = 'métodos de pago'
        constraints = [
            models.UniqueConstraint(fields=['nombre'], name='UQ_METODOS_NOMBRE'),
        ]

    def __str__(self):
        return self.nombre
