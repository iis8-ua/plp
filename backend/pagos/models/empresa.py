"""Empresas que cobran a través de la pasarela."""

import uuid

from django.db import models


class Empresa(models.Model):
    class Estado(models.TextChoices):
        ACTIVA = 'activo', 'Activa'
        BAJA = 'dado-de-baja', 'Dada de baja'

    id = models.UUIDField(
        'identificador', primary_key=True, default=uuid.uuid4, editable=False,
        db_column='ID',
    )
    nombre = models.CharField('nombre', max_length=100, db_column='NOMBRE')
    fecha_registro = models.DateTimeField(
        'fecha de registro', auto_now_add=True, db_column='FECHA_REGISTRO'
    )
    estado = models.CharField(
        'estado', max_length=12, choices=Estado, default=Estado.ACTIVA,
        db_column='ESTADO',
    )
    razon_social = models.CharField(
        'razón social', max_length=150, blank=True, default='', db_column='RAZON_SOCIAL'
    )
    cif = models.CharField('CIF/NIF', max_length=20, blank=True, default='', db_column='CIF')
    tipo_empresa = models.CharField(
        'tipo de empresa', max_length=40, blank=True, default='', db_column='TIPO_EMPRESA'
    )
    actividad_economica = models.CharField(
        'actividad económica', max_length=150, blank=True, default='',
        db_column='ACTIVIDAD_ECONOMICA',
    )
    direccion = models.CharField(
        'dirección fiscal', max_length=200, blank=True, default='', db_column='DIRECCION'
    )
    codigo_postal = models.CharField(
        'código postal', max_length=10, blank=True, default='', db_column='CODIGO_POSTAL'
    )
    ciudad = models.CharField('ciudad', max_length=80, blank=True, default='', db_column='CIUDAD')
    provincia = models.CharField(
        'provincia', max_length=80, blank=True, default='', db_column='PROVINCIA'
    )
    pais = models.CharField(
        'país', max_length=80, blank=True, default='España', db_column='PAIS'
    )
    telefono = models.CharField(
        'teléfono', max_length=30, blank=True, default='', db_column='TELEFONO'
    )
    email = models.EmailField('correo', max_length=150, blank=True, default='', db_column='EMAIL')
    web = models.CharField('web', max_length=200, blank=True, default='', db_column='WEB')

    class Meta:
        db_table = 'EMPRESAS'
        ordering = ['nombre']
        verbose_name = 'empresa'
        verbose_name_plural = 'empresas'

    def __str__(self):
        return self.nombre
