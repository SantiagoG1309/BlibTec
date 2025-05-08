from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Prestamo
from .forms import PrestamoForm
from libros.models import Libro
from historial.models import Historial

@login_required
def lista_prestamos(request):
    if not (request.user.is_admin or request.user.is_superadmin):
        messages.error(request, 'No tienes permisos para gestionar préstamos.')
        return redirect('libros:lista')
    
    prestamos_activos = Prestamo.objects.filter(estado='APROBADO')
    prestamos_pendientes = Prestamo.objects.filter(estado='PENDIENTE')
    return render(request, 'prestamos/lista_prestamos.html', {
        'prestamos_activos': prestamos_activos,
        'prestamos_pendientes': prestamos_pendientes
    })

@login_required
def detalle_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    if not (request.user.is_admin or request.user.is_superadmin or request.user == prestamo.usuario):
        messages.error(request, 'No tienes permisos para ver este préstamo.')
        return redirect('libros:lista')
    return render(request, 'prestamos/detalle_prestamo.html', {'prestamo': prestamo})

@login_required
def solicitar_prestamo(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    if request.user.rol not in ['CLIENTE']:
        messages.error(request, 'Solo los clientes pueden solicitar préstamos.')
        return redirect('libros:lista')

    if libro.estado != 'DISPONIBLE' or libro.cantidad_total <= 0:
        messages.error(request, 'Este libro no está disponible para préstamo.')
        return redirect('libros:lista')

    if Prestamo.objects.filter(usuario=request.user, libro=libro, estado__in=['PENDIENTE', 'APROBADO']).exists():
        messages.error(request, 'Ya tienes un préstamo pendiente o activo para este libro.')
        return redirect('libros:lista')

    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        if form.is_valid():
            prestamo = Prestamo(
                usuario=request.user,
                libro=libro,
                estado='PENDIENTE',
                fecha_solicitud=timezone.now()
            )
            prestamo.save()
            Historial.registrar_cambio(request.user, 'PRESTAMO', 'CREACION', prestamo.id, f'Solicitud de préstamo para {libro.titulo}')
            messages.success(request, 'Solicitud de préstamo enviada exitosamente.')
            return redirect('prestamos:mis_prestamos')
    else:
        form = PrestamoForm()

    return render(request, 'prestamos/solicitar_prestamo.html', {'form': form, 'libro': libro})

@login_required
def aprobar_prestamo(request, prestamo_id):
    if not (request.user.is_admin or request.user.is_superadmin):
        messages.error(request, 'No tienes permisos para aprobar préstamos.')
        return redirect('libros:lista')

    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    if prestamo.estado != 'PENDIENTE':
        messages.error(request, 'Este préstamo no está pendiente de aprobación.')
        return redirect('prestamos:lista_prestamos')

    if prestamo.libro.cantidad_total <= 0:
        messages.error(request, 'No hay libros disponibles para aprobar este préstamo.')
        return redirect('prestamos:lista_prestamos')

    prestamo.aprobar(administrador=request.user)
    Historial.registrar_cambio(request.user, 'PRESTAMO', 'CAMBIO_ESTADO', prestamo.id, f'Aprobado préstamo para {prestamo.libro.titulo}', 'PENDIENTE', 'APROBADO')
    messages.success(request, 'Préstamo aprobado exitosamente.')
    return redirect('prestamos:lista_prestamos')

@login_required
def rechazar_prestamo(request, prestamo_id):
    if not (request.user.is_admin or request.user.is_superadmin):
        messages.error(request, 'No tienes permisos para rechazar préstamos.')
        return redirect('libros:lista')

    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    if prestamo.estado != 'PENDIENTE':
        messages.error(request, 'Este préstamo no está pendiente de aprobación.')
        return redirect('prestamos:lista_prestamos')

    if request.method == 'POST':
        motivo = request.POST.get('motivo', 'No especificado')
        prestamo.rechazar(administrador=request.user, motivo=motivo)
        Historial.registrar_cambio(request.user, 'PRESTAMO', 'CAMBIO_ESTADO', prestamo.id, f'Rechazado préstamo para {prestamo.libro.titulo} ({motivo})', 'PENDIENTE', 'RECHAZADO')
        messages.success(request, 'Préstamo rechazado exitosamente.')
        return redirect('prestamos:lista_prestamos')

    return render(request, 'prestamos/rechazar_prestamo.html', {'prestamo': prestamo})

@login_required
def devolver_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    if not (request.user.is_admin or request.user.is_superadmin or request.user == prestamo.usuario):
        messages.error(request, 'No tienes permisos para devolver este préstamo.')
        return redirect('libros:lista')

    if prestamo.devolver():
        Historial.registrar_cambio(request.user, 'PRESTAMO', 'CAMBIO_ESTADO', prestamo.id, f'Devuelto préstamo para {prestamo.libro.titulo}', 'APROBADO', 'DEVUELTO')
        messages.success(request, 'Préstamo devuelto exitosamente.')
    else:
        messages.error(request, 'No se pudo devolver el préstamo. Asegúrate de que esté aprobado.')
    return redirect('prestamos:mis_prestamos')

@login_required
def mis_prestamos(request):
    prestamos = Prestamo.objects.filter(
        usuario=request.user,
        estado__in=['PENDIENTE', 'APROBADO']
    ).order_by('-fecha_solicitud')
    return render(request, 'prestamos/mis_prestamos.html', {'prestamos': prestamos})

@login_required
def cliente_historial_prestamos(request):
    if request.user.rol not in ['CLIENTE']:
        messages.error(request, 'Solo los clientes pueden ver este historial.')
        return redirect('libros:lista')

    historial = Historial.objects.filter(
        usuario=request.user,
        tipo_entidad='PRESTAMO'
    ).order_by('-fecha')

    registros = []
    for registro in historial:
        try:
            entidad = Prestamo.objects.get(id=registro.entidad_id)
            registros.append({
                'fecha': registro.fecha,
                'usuario': registro.usuario,
                'tipo_entidad': registro.tipo_entidad,
                'entidad': entidad,
                'tipo_accion': registro.tipo_accion.lower(),
                'estado_anterior': registro.estado_anterior,
                'estado_nuevo': registro.estado_nuevo,
                'detalles': registro.detalles,
                'prestamo': entidad,
            })
        except Prestamo.DoesNotExist:
            continue

    paginator = Paginator(registros, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'prestamos/cliente_historial_prestamos.html', {
        'registros': page_obj,
        'page_obj': page_obj,
        'total_registros': len(registros),
        'is_paginated': page_obj.has_previous() or page_obj.has_next(),
    })