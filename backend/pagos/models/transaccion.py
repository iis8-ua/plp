"""Transacciones cobradas por una empresa."""

import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q

from .empresa import Empresa
from .informacion_pago import InformacionPago
from .moneda import Moneda


class Transaccion(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        APROBADA = 'APROBADA', 'Aprobada'
        RECHAZADA = 'RECHAZADA', 'Rechazada'
        REEMBOLSADA = 'REEMBOLSADA', 'Reembolsada'

    id = models.UUIDField(
        'identificador', primary_key=True, default=uuid.uuid4, editable=False,
        db_column='ID',
    )
    receptor = models.ForeignKey(
        Empresa, on_delete=models.PROTECT, db_column='RECEPTOR_ID',
        related_name='transacciones', verbose_name='receptor',
    )
    informacion = models.OneToOneField(
        InformacionPago, on_delete=models.PROTECT, db_column='INFORMACION_ID',
        related_name='transaccion', verbose_name='información de pago',
    )
    concepto = models.CharField('concepto', max_length=255, db_column='CONCEPTO')
    cantidad = models.DecimalField(
        'cantidad', max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))], db_column='CANTIDAD',
    )
    comision = models.DecimalField(
        'comisión', max_digits=12, decimal_places=2, default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))], db_column='COMISION',
    )
    moneda = models.ForeignKey(
        Moneda, on_delete=models.PROTECT, db_column='MONEDA', verbose_name='moneda'
    )
    estado = models.CharField(
        'estado', max_length=11, choices=Estado, default=Estado.PENDIENTE,
        db_column='ESTADO',
    )
    fecha = models.DateTimeField('fecha', auto_now_add=True, db_column='FECHA')
    num_factura = models.CharField(
        'número de factura', max_length=30, null=True, blank=True,
        db_column='NUM_FACTURA',
    )
    referencia = models.CharField(
        'referencia', max_length=20, null=True, blank=True, db_column='REFERENCIA',
        help_text='Identificador corto del pago (por ejemplo, P-1048).',
    )
    motivo = models.CharField(
        'motivo', max_length=255, blank=True, default='', db_column='MOTIVO',
        help_text='Último motivo registrado para el estado del pago.',
    )

    class Meta:
        db_table = 'TRANSACCIONES'
        ordering = ['-fecha']
        verbose_name = 'transacción'
        verbose_name_plural = 'transacciones'
        constraints = [
            models.CheckConstraint(
                condition=Q(cantidad__gt=0), name='CHK_TX_CANTIDAD'
            ),
            models.CheckConstraint(
                condition=Q(comision__gte=0) & Q(comision__lte=F('cantidad')),
                name='CHK_TX_COMISION',
            ),
            # La numeración de facturas es una serie por empresa. Como en MySQL
            # y SQLite los NULL no colisionan en un UNIQUE, los pagos sin
            # factura pueden compartir NUM_FACTURA nulo.
            models.UniqueConstraint(
                fields=['receptor', 'num_factura'], name='UQ_TX_FACTURA'
            ),
        ]

    def __str__(self):
        return f'{self.id} ({self.cantidad} {self.moneda_id})'
