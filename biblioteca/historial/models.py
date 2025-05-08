from django.db import models
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from aldjemy.meta import AldjemyMeta
from usuarios.models import Usuario
from libros.models import Libro
from prestamos.models import Prestamo

class Historial(models.Model, metaclass=AldjemyMeta):
    TIPOS_ENTIDAD = [
        ('LIBRO', 'Libro'),
        ('PRESTAMO', 'Préstamo'),
        ('USUARIO', 'Usuario'),
    ]

    TIPOS_ACCION = [
        ('CREACION', 'Creación'),
        ('MODIFICACION', 'Modificación'),
        ('ELIMINACION', 'Eliminación'),
        ('CAMBIO_ESTADO', 'Cambio de Estado'),
    ]

    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='acciones_historial')
    tipo_entidad = models.CharField(max_length=20, choices=TIPOS_ENTIDAD)
    tipo_accion = models.CharField(max_length=20, choices=TIPOS_ACCION)
    entidad_id = models.IntegerField()
    detalles = models.TextField()
    estado_anterior = models.CharField(max_length=50, blank=True, null=True)
    estado_nuevo = models.CharField(max_length=50, blank=True, null=True)

    __sa_columns__ = [
        Column('fecha', DateTime),
        Column('usuario_id', Integer, ForeignKey('usuarios.id')),
        Column('tipo_entidad', String(20)),
        Column('tipo_accion', String(20)),
        Column('entidad_id', Integer),
        Column('detalles', Text),
        Column('estado_anterior', String(50)),
        Column('estado_nuevo', String(50))
    ]

    class Meta:
        db_table = 'historial'
        verbose_name = 'Registro de Historial'
        verbose_name_plural = 'Registros de Historial'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_tipo_accion_display()} de {self.get_tipo_entidad_display()} - {self.fecha}'

    @classmethod
    def registrar_cambio(cls, usuario, tipo_entidad, tipo_accion, entidad_id, detalles, estado_anterior=None, estado_nuevo=None):
        return cls.objects.create(
            usuario=usuario,
            tipo_entidad=tipo_entidad,
            tipo_accion=tipo_accion,
            entidad_id=entidad_id,
            detalles=detalles,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo
        )
