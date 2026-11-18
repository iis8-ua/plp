"""Información de pago (método + titular) asociada a una transacción."""

import uuid

from django.db import models

from .metodo_pago import MetodoPago


class InformacionPago(models.Model):
    id = models.UUIDField(
        'identificador', primary_key=True, default=uuid.uuid4, editable=False,
        db_column='ID',
    )
    metodo = models.ForeignKey(
        MetodoPago, on_delete=models.PROTECT, db_column='METODO_ID',
        related_name='informaciones', verbose_name='método de pago',
    )
    titular = models.CharField('titular', max_length=100, db_column='TITULAR')

    class Meta:
        db_table = 'INFORMACION_PAGOS'
        verbose_name = 'información de pago'
        verbose_name_plural = 'informaciones de pago'

    def __str__(self):
        return f'{self.titular} ({self.metodo})'
