from django.db import models
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from aldjemy.meta import AldjemyMeta
from usuarios.models import Usuario
from libros.models import Libro
from django.utils import timezone
from datetime import timedelta

class Prestamo(models.Model, metaclass=AldjemyMeta):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de Aprobación'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('DEVUELTO', 'Devuelto'),
        ('VENCIDO', 'Vencido'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='prestamos')
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='prestamos')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_devolucion_esperada = models.DateTimeField(null=True, blank=True)
    fecha_devolucion_real = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    aprobado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='prestamos_aprobados')
    notas = models.TextField(blank=True)

    __sa_columns__ = [
        Column('usuario_id', Integer, ForeignKey('usuarios.id')),
        Column('libro_id', Integer, ForeignKey('libros.id')),
        Column('fecha_solicitud', DateTime),
        Column('fecha_aprobacion', DateTime),
        Column('fecha_devolucion_esperada', DateTime),
        Column('fecha_devolucion_real', DateTime),
        Column('estado', String(20)),
        Column('aprobado_por_id', Integer, ForeignKey('usuarios.id')),
        Column('notas', String)
    ]

    class Meta:
        db_table = 'prestamos'
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'
        ordering = ['-fecha_aprobacion']

    def __str__(self):
        return f'Préstamo de {self.libro.titulo} a {self.usuario.username}'

    def aprobar(self, administrador):
        if self.estado == 'PENDIENTE' and self.libro.cantidad_total > 0:
            self.estado = 'APROBADO'
            self.aprobado_por = administrador
            self.fecha_aprobacion = timezone.now()
            self.fecha_devolucion_esperada = self.fecha_aprobacion + timedelta(days=15)
            self.libro.cantidad_total -= 1
            self.libro.actualizar_disponibilidad()
            self.libro.save()
            self.save()
            return True
        return False

    def rechazar(self, administrador, motivo):
        if self.estado == 'PENDIENTE':
            self.estado = 'RECHAZADO'
            self.aprobado_por = administrador
            self.notas = motivo
            self.save()
            return True
        return False

    def devolver(self):
        if self.estado == 'APROBADO':
            self.estado = 'DEVUELTO'
            self.fecha_devolucion_real = timezone.now()
            self.libro.cantidad_total += 1
            self.libro.actualizar_disponibilidad()
            self.libro.save()
            self.save()
            return True
        return False