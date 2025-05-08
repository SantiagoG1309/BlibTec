from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Historial
from libros.models import Libro
from usuarios.models import Usuario
from prestamos.models import Prestamo

@login_required
def lista_historial(request):
    if not request.user.is_admin() and not request.user.is_superadmin():
        messages.error(request, 'No tienes permisos para ver el historial.')
        return redirect('usuarios:perfil')
    
    historial = Historial.objects.all().order_by('-fecha')
    registros = []
    for registro in historial:
        # Obtener la entidad relacionada según tipo_entidad y entidad_id
        entidad = None
        if registro.tipo_entidad == 'LIBRO':
            try:
                entidad = Libro.objects.get(id=registro.entidad_id)
            except Libro.DoesNotExist:
                entidad = None
        elif registro.tipo_entidad == 'PRESTAMO':
            try:
                entidad = Prestamo.objects.get(id=registro.entidad_id)
            except Prestamo.DoesNotExist:
                entidad = None
        elif registro.tipo_entidad == 'USUARIO':
            try:
                entidad = Usuario.objects.get(id=registro.entidad_id)
            except Usuario.DoesNotExist:
                entidad = None
        
        registros.append({
            'fecha': registro.fecha,
            'usuario': registro.usuario,
            'tipo_entidad': registro.tipo_entidad,
            'entidad': entidad,
            'tipo_accion': registro.tipo_accion.lower(),
            'estado_anterior': registro.estado_anterior,
            'estado_nuevo': registro.estado_nuevo,
            'detalles': registro.detalles,
            'prestamo': entidad if registro.tipo_entidad == 'PRESTAMO' else None,
        })

    paginator = Paginator(registros, 20)  # 20 registros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'historial/lista_historial.html', {
        'registros': page_obj,
        'page_obj': page_obj,
        'total_registros': len(registros),
        'is_paginated': page_obj.has_previous() or page_obj.has_next(),
    })

@login_required
def historial_por_entidad(request, tipo_entidad, entidad_id):
    if not request.user.is_admin() and not request.user.is_superadmin():
        messages.error(request, 'No tienes permisos para ver el historial.')
        return redirect('usuarios:perfil')
    
    # Normalizar tipo_entidad para que coincida con los valores del modelo
    tipo_entidad = tipo_entidad.upper()
    if tipo_entidad not in dict(Historial.TIPOS_ENTIDAD):
        messages.error(request, 'Tipo de entidad no válido.')
        return redirect('historial:lista_historial')

    historial = Historial.objects.filter(
        tipo_entidad=tipo_entidad,
        entidad_id=entidad_id
    ).order_by('-fecha')

    registros = []
    for registro in historial:
        # Obtener la entidad relacionada
        entidad = None
        if registro.tipo_entidad == 'LIBRO':
            try:
                entidad = Libro.objects.get(id=registro.entidad_id)
            except Libro.DoesNotExist:
                entidad = None
        elif registro.tipo_entidad == 'PRESTAMO':
            try:
                entidad = Prestamo.objects.get(id=registro.entidad_id)
            except Prestamo.DoesNotExist:
                entidad = None
        elif registro.tipo_entidad == 'USUARIO':
            try:
                entidad = Usuario.objects.get(id=registro.entidad_id)
            except Usuario.DoesNotExist:
                entidad = None
        
        registros.append({
            'fecha': registro.fecha,
            'usuario': registro.usuario,
            'tipo_entidad': registro.tipo_entidad,
            'entidad': entidad,
            'tipo_accion': registro.tipo_accion.lower(),
            'estado_anterior': registro.estado_anterior,
            'estado_nuevo': registro.estado_nuevo,
            'detalles': registro.detalles,
            'prestamo': entidad if registro.tipo_entidad == 'PRESTAMO' else None,
        })

    paginator = Paginator(registros, 20)  # 20 registros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'historial/lista_historial.html', {
        'registros': page_obj,
        'page_obj': page_obj,
        'total_registros': len(registros),
        'tipo_entidad': tipo_entidad,
        'entidad_id': entidad_id,
        'is_paginated': page_obj.has_previous() or page_obj.has_next(),
    })