from django.contrib.auth.models import AbstractUser
from django.db import models
from sqlalchemy import Column, Integer, String, Enum
from aldjemy.meta import AldjemyMeta

class Usuario(AbstractUser, metaclass=AldjemyMeta):
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='usuario_set',
        related_query_name='usuario'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='usuario_set',
        related_query_name='usuario'
    )
    
    ROLES = [
        ('CLIENTE', 'Cliente'),
        ('ADMINISTRADOR', 'Administrador'),
        ('SUPERADMINISTRADOR', 'Super Administrador'),
    ]

    rol = models.CharField(max_length=20, choices=ROLES, default='CLIENTE')
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.TextField(blank=True)

    __sa_columns__ = [
        Column('rol', String(20)),
        Column('telefono', String(15)),
        Column('direccion', String),
    ]

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.username} - {self.get_rol_display()}'

    def is_superadmin(self):
        return self.rol == 'SUPERADMINISTRADOR'

    def is_admin(self):
        return self.rol == 'ADMINISTRADOR'

    def is_cliente(self):
        return self.rol == 'CLIENTE'
