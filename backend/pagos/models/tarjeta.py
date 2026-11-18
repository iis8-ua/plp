"""Tarjeta asociada a una información de pago.

La PK es también la FK a ``INFORMACION_PAGOS`` (relación 1:1).
"""

from django.db import models

from .informacion_pago import InformacionPago


class Tarjeta(models.Model):
    informacion = models.OneToOneField(
        InformacionPago, on_delete=models.CASCADE, primary_key=True,
        db_column='ID', related_name='tarjeta',
        verbose_name='información de pago',
    )
    marca = models.CharField('marca', max_length=20, db_column='MARCA')
    ultimos4 = models.CharField('últimos 4 dígitos', max_length=4, db_column='ULTIMOS4')
    caducidad = models.CharField('caducidad', max_length=5, db_column='CADUCIDAD')
    token = models.CharField('token', max_length=64, db_column='TOKEN')

    class Meta:
        db_table = 'TARJETAS'
        verbose_name = 'tarjeta'
        verbose_name_plural = 'tarjetas'
        constraints = [
            models.UniqueConstraint(fields=['token'], name='UQ_TARJETAS_TOKEN'),
        ]

    def __str__(self):
        return f'{self.marca} ****{self.ultimos4}'
