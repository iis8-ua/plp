"""Catálogo de monedas (código ISO de 3 letras)."""

from django.db import models


class Moneda(models.Model):
    codigo = models.CharField(
        'código', max_length=3, primary_key=True, db_column='CODIGO'
    )
    nombre = models.CharField('nombre', max_length=30, db_column='NOMBRE')
    decimales = models.PositiveSmallIntegerField(
        'decimales', default=2, db_column='DECIMALES'
    )

    class Meta:
        db_table = 'MONEDAS'
        ordering = ['codigo']
        verbose_name = 'moneda'
        verbose_name_plural = 'monedas'

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'
