"""Solicitudes de reembolso sobre una transacción."""

import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from .transaccion import Transaccion


class Reembolso(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        ACEPTADO = 'ACEPTADO', 'Aceptado'
        RECHAZADO = 'RECHAZADO', 'Rechazado'

    id = models.UUIDField(
        'identificador', primary_key=True, default=uuid.uuid4, editable=False,
        db_column='ID',
    )
    transaccion = models.ForeignKey(
        Transaccion, on_delete=models.PROTECT, db_column='TRANSACCION_ID',
        related_name='reembolsos', verbose_name='transacción',
    )
    cantidad = models.DecimalField(
        'cantidad', max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))], db_column='CANTIDAD',
    )
    fecha = models.DateTimeField('fecha', auto_now_add=True, db_column='FECHA')
    motivo = models.CharField(
        'motivo', max_length=255, null=True, blank=True, db_column='MOTIVO'
    )
    # No está en el diagrama original, pero /refunds/accept y /refunds/reject
    # necesitan guardar la decisión sobre la solicitud.
    estado = models.CharField(
        'estado', max_length=9, choices=Estado, default=Estado.PENDIENTE,
        db_column='ESTADO',
    )

    class Meta:
        db_table = 'REEMBOLSOS'
        ordering = ['-fecha']
        verbose_name = 'reembolso'
        verbose_name_plural = 'reembolsos'
        constraints = [
            models.CheckConstraint(
                condition=Q(cantidad__gt=0), name='CHK_REEMBOLSOS_CANTIDAD'
            ),
        ]

    def __str__(self):
        return f'{self.id} ({self.cantidad})'
