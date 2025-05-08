from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Libro
from .forms import LibroForm
from historial.models import Historial

@login_required
def lista_libros(request):
    libros = Libro.objects.all()
    return render(request, 'libros/lista_libros.html', {'libros': libros})

@login_required
def buscar_libros(request):
    query = request.GET.get('q', '')
    if query:
        libros = Libro.objects.filter(
            Q(titulo__icontains=query) |
            Q(autor__icontains=query)
        )
    else:
        libros = Libro.objects.all()
    return render(request, 'libros/lista_libros.html', {'libros': libros, 'query': query})

@login_required
def detalle_libro(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    return render(request, 'libros/detalle_libro.html', {'libro': libro})

@login_required
def gestionar_libro(request, libro_id=None):
    if not (request.user.is_admin or request.user.is_superadmin):
        messages.error(request, 'No tienes permisos para gestionar libros.')
        return redirect('libros:lista')

    if request.method == 'POST':
        if libro_id:  # Edición o eliminación
            libro = get_object_or_404(Libro, id=libro_id)
            form = LibroForm(request.POST, instance=libro)
            accion = request.POST.get('accion')
            if accion == 'editar':
                if form.is_valid():
                    libro_actualizado = form.save()
                    Historial.registrar_cambio(
                        usuario=request.user,
                        tipo_entidad='LIBRO',
                        tipo_accion='MODIFICACION',
                        entidad_id=libro.id,
                        detalles=f'Actualización del libro: {libro.titulo}'
                    )
                    messages.success(request, 'Libro actualizado exitosamente.')
                    return redirect('libros:detalle', libro_id=libro.id)
            elif accion == 'eliminar':
                try:
                    titulo_libro = libro.titulo
                    libro.delete()
                    Historial.registrar_cambio(
                        usuario=request.user,
                        tipo_entidad='LIBRO',
                        tipo_accion='ELIMINACION',
                        entidad_id=libro_id,
                        detalles=f'Eliminación del libro: {titulo_libro}'
                    )
                    messages.success(request, 'Libro eliminado exitosamente.')
                    return redirect('libros:lista')
                except Exception as e:
                    messages.error(request, f'Error al eliminar el libro: {str(e)}')
                    return redirect('libros:lista')
            else:
                messages.error(request, 'Acción no válida.')
                return redirect('libros:lista')
        else:  # Creación
            form = LibroForm(request.POST)
            if form.is_valid():
                libro = form.save(commit=False)
                libro.registrado_por = request.user
                libro.estado = 'DISPONIBLE'
                libro.save()
                Historial.registrar_cambio(
                    usuario=request.user,
                    tipo_entidad='LIBRO',
                    tipo_accion='CREACION',
                    entidad_id=libro.id,
                    detalles=f'Creación del libro: {libro.titulo}'
                )
                messages.success(request, 'Libro creado exitosamente.')
                return redirect('libros:detalle', libro_id=libro.id)
        messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = LibroForm(instance=get_object_or_404(Libro, id=libro_id) if libro_id else None)

    return render(request, 'libros/form_libro.html', {
        'form': form,
        'libro_id': libro_id,
        'es_edicion': libro_id is not None
    })