"""Cuenta bancaria asociada a una información de pago.

La PK es también la FK a ``INFORMACION_PAGOS`` (relación 1:1).
"""

from django.db import models

from .informacion_pago import InformacionPago


class CuentaBancaria(models.Model):
    informacion = models.OneToOneField(
        InformacionPago, on_delete=models.CASCADE, primary_key=True,
        db_column='ID', related_name='cuenta_bancaria',
        verbose_name='información de pago',
    )
    iban = models.CharField('IBAN', max_length=34, db_column='IBAN')

    class Meta:
        db_table = 'CUENTAS_BANCARIAS'
        verbose_name = 'cuenta bancaria'
        verbose_name_plural = 'cuentas bancarias'

    def __str__(self):
        return self.iban
