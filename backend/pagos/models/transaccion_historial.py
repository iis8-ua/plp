"""Historial de estados de una transacción."""

import uuid

from django.db import models

from .transaccion import Transaccion


class TransaccionHistorial(models.Model):
    id = models.UUIDField(
        'identificador', primary_key=True, default=uuid.uuid4, editable=False,
        db_column='ID',
    )
    transaccion = models.ForeignKey(
        Transaccion, on_delete=models.CASCADE, db_column='TRANSACCION_ID',
        related_name='historial', verbose_name='transacción',
    )
    estado = models.CharField(
        'estado', max_length=11, choices=Transaccion.Estado.choices,
        db_column='ESTADO',
    )
    motivo = models.CharField(
        'motivo', max_length=255, blank=True, default='', db_column='MOTIVO'
    )
    fecha = models.DateTimeField('fecha', auto_now_add=True, db_column='FECHA')

    class Meta:
        db_table = 'TRANSACCION_HISTORIAL'
        ordering = ['fecha']
        verbose_name = 'evento de transacción'
        verbose_name_plural = 'eventos de transacción'

    def __str__(self):
        return f'{self.transaccion_id}: {self.estado} ({self.motivo})'
