from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Libro, Categoria
from .forms import LibroForm, CategoriaForm
from historial.models import Historial

@login_required
def lista_libros(request):
    libros = Libro.objects.all()
    categorias = Categoria.objects.all().order_by('nombre')
    return render(request, 'libros/lista_libros.html', {
        'libros': libros,
        'categorias': categorias,
        'query': '',
        'categoria_seleccionada': ''
    })

@login_required
def buscar_libros(request):
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    
    libros = Libro.objects.all()
    categorias = Categoria.objects.all().order_by('nombre')
    
    if query:
        libros = libros.filter(
            Q(titulo__icontains=query) |
            Q(autor__icontains=query)
        )
    
    if categoria_id:
        try:
            categoria_id = int(categoria_id)
            libros = libros.filter(categoria_id=categoria_id)
        except (ValueError, TypeError):
            messages.error(request, 'Categoría no válida.')
    
    return render(request, 'libros/lista_libros.html', {
        'libros': libros,
        'query': query,
        'categorias': categorias,
        'categoria_seleccionada': categoria_id
    })

@login_required
def detalle_libro(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    return render(request, 'libros/detalle_libro.html', {'libro': libro})

@login_required
def gestionar_categorias(request):
    if not (request.user.is_admin or request.user.is_superadmin):
        messages.error(request, 'No tienes permisos para gestionar categorías.')
        return redirect('libros:lista')

    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            Historial.registrar_cambio(
                usuario=request.user,
                tipo_entidad='CATEGORIA',
                tipo_accion='CREACION',
                entidad_id=categoria.id,
                detalles=f'Creación de la categoría: {categoria.nombre}'
            )
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('libros:gestionar_categorias')
    else:
        form = CategoriaForm()

    categorias = Categoria.objects.all().order_by('nombre')
    return render(request, 'libros/gestionar_categorias.html', {
        'form': form,
        'categorias': categorias
    })

@login_required
def editar_categoria(request, categoria_id):
    if not (request.user.is_admin or request.user.is_superadmin):
        messages.error(request, 'No tienes permisos para editar categorías.')
        return redirect('libros:lista')

    categoria = get_object_or_404(Categoria, id=categoria_id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            categoria = form.save()
            Historial.registrar_cambio(
                usuario=request.user,
                tipo_entidad='CATEGORIA',
                tipo_accion='MODIFICACION',
                entidad_id=categoria.id,
                detalles=f'Actualización de la categoría: {categoria.nombre}'
            )
            messages.success(request, 'Categoría actualizada exitosamente.')
            return redirect('libros:gestionar_categorias')
    return redirect('libros:gestionar_categorias')

@login_required
def eliminar_categoria(request, categoria_id):
    if not (request.user.is_admin or request.user.is_superadmin):
        messages.error(request, 'No tienes permisos para eliminar categorías.')
        return redirect('libros:lista')

    categoria = get_object_or_404(Categoria, id=categoria_id)
    if request.method == 'POST':
        try:
            categoria.delete()
            Historial.registrar_cambio(
                usuario=request.user,
                tipo_entidad='CATEGORIA',
                tipo_accion='ELIMINACION',
                entidad_id=categoria.id,
                detalles=f'Eliminación de la categoría: {categoria.nombre}'
            )
            messages.success(request, 'Categoría eliminada exitosamente.')
        except Exception as e:
            messages.error(request, 'No se puede eliminar la categoría porque hay libros asociados a ella.')
    return redirect('libros:gestionar_categorias')

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
                if not form.cleaned_data['categoria']:
                    messages.error(request, 'Debes seleccionar una categoría.')
                else:
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
            else:
                messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = LibroForm(instance=get_object_or_404(Libro, id=libro_id) if libro_id else None)

    return render(request, 'libros/form_libro.html', {
        'form': form,
        'libro_id': libro_id,
        'es_edicion': libro_id is not None
    })