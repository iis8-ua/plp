"""Tickets de soporte y su conversación."""

import uuid

from django.conf import settings
from django.db import models

from .empresa import Empresa


class Ticket(models.Model):
    class Estado(models.TextChoices):
        ABIERTO = 'ABIERTO', 'Abierto'
        EN_PROCESO = 'EN_PROCESO', 'En proceso'
        CERRADO = 'CERRADO', 'Cerrado'

    id = models.UUIDField(
        'identificador', primary_key=True, default=uuid.uuid4, editable=False,
        db_column='ID',
    )
    numero = models.PositiveIntegerField(
        'número', unique=True, db_column='NUMERO',
        help_text='Identificador visible del ticket (por ejemplo, 1086).',
    )
    empresa = models.ForeignKey(
        Empresa, on_delete=models.PROTECT, db_column='EMPRESA_ID',
        related_name='tickets', verbose_name='empresa',
    )
    asunto = models.CharField('asunto', max_length=140, db_column='ASUNTO')
    descripcion = models.TextField('descripción', blank=True, db_column='DESCRIPCION')
    estado = models.CharField(
        'estado', max_length=10, choices=Estado, default=Estado.ABIERTO,
        db_column='ESTADO',
    )
    tecnico = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        db_column='TECNICO_ID', related_name='tickets_asignados',
        verbose_name='técnico asignado',
    )
    creado = models.DateTimeField('creado', auto_now_add=True, db_column='CREADO')
    actualizado = models.DateTimeField(
        'actualizado', auto_now=True, db_column='ACTUALIZADO'
    )

    class Meta:
        db_table = 'TICKETS'
        ordering = ['-actualizado']
        verbose_name = 'ticket'
        verbose_name_plural = 'tickets'

    def __str__(self):
        return f'#{self.numero} - {self.asunto}'


class TicketMensaje(models.Model):
    class Rol(models.TextChoices):
        COMERCIO = 'comercio', 'Comercio'
        TECNICO = 'tecnico', 'Técnico'

    id = models.UUIDField(
        'identificador', primary_key=True, default=uuid.uuid4, editable=False,
        db_column='ID',
    )
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, db_column='TICKET_ID',
        related_name='mensajes', verbose_name='ticket',
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column='AUTOR_ID',
        related_name='mensajes_ticket', verbose_name='autor',
    )
    rol = models.CharField(
        'rol', max_length=8, choices=Rol, db_column='ROL'
    )
    mensaje = models.TextField('mensaje', db_column='MENSAJE')
    creado = models.DateTimeField('creado', auto_now_add=True, db_column='CREADO')

    class Meta:
        db_table = 'TICKET_MENSAJES'
        ordering = ['creado']
        verbose_name = 'mensaje de ticket'
        verbose_name_plural = 'mensajes de ticket'

    def __str__(self):
        return f'{self.ticket_id}: {self.mensaje[:40]}'


class TicketHistorial(models.Model):
    id = models.UUIDField(
        'identificador', primary_key=True, default=uuid.uuid4, editable=False,
        db_column='ID',
    )
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, db_column='TICKET_ID',
        related_name='historial', verbose_name='ticket',
    )
    titulo = models.CharField('título', max_length=100, db_column='TITULO')
    descripcion = models.TextField('descripción', blank=True, db_column='DESCRIPCION')
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        db_column='AUTOR_ID', related_name='historial_tickets', verbose_name='autor',
    )
    fecha = models.DateTimeField('fecha', auto_now_add=True, db_column='FECHA')

    class Meta:
        db_table = 'TICKET_HISTORIAL'
        ordering = ['fecha']
        verbose_name = 'evento de ticket'
        verbose_name_plural = 'eventos de ticket'

    def __str__(self):
        return f'{self.ticket_id}: {self.titulo}'
