"""Saldo de una empresa en una moneda concreta (PK compuesta)."""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from .empresa import Empresa
from .moneda import Moneda


class SaldoEmpresa(models.Model):
    pk = models.CompositePrimaryKey('empresa', 'moneda')
    empresa = models.ForeignKey(
        Empresa, on_delete=models.PROTECT, db_column='EMPRESA_ID',
        related_name='saldos', verbose_name='empresa',
    )
    moneda = models.ForeignKey(
        Moneda, on_delete=models.PROTECT, db_column='MONEDA',
        related_name='saldos', verbose_name='moneda',
    )
    saldo = models.DecimalField(
        'saldo', max_digits=12, decimal_places=2, default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))], db_column='SALDO',
    )

    class Meta:
        db_table = 'SALDOS_EMPRESAS'
        verbose_name = 'saldo de empresa'
        verbose_name_plural = 'saldos de empresas'
        constraints = [
            models.CheckConstraint(
                condition=Q(saldo__gte=0), name='CHK_SALDOS_NO_NEGATIVO'
            ),
        ]

    def __str__(self):
        return f'{self.empresa} - {self.moneda_id}: {self.saldo}'
