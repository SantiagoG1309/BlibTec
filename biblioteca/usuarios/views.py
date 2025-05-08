from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario
from .forms import RegistroUsuarioForm, ActualizarPerfilForm, LoginForm, RegistroAdminForm
from historial.models import Historial
from prestamos.models import Prestamo
from django.utils import timezone

def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            Historial.registrar_cambio(
                usuario=usuario,
                tipo_entidad='USUARIO',
                tipo_accion='CREACION',
                entidad_id=usuario.id,
                detalles=f'Registro de nuevo usuario: {usuario.username}'
            )
            messages.success(request, 'Registro exitoso. Por favor, inicia sesión.')
            return redirect('usuarios:login')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'usuarios/registro.html', {'form': form})

def login_usuario(request):
    if request.user.is_authenticated:
        if request.user.rol == 'CLIENTE':
            return redirect('libros:lista')
        return redirect('usuarios:perfil')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido, {user.username}!')
                next_url = request.POST.get('next', '')
                if next_url:
                    return redirect(next_url)
                if user.rol == 'CLIENTE':
                    return redirect('libros:lista')
                elif user.rol in ['ADMINISTRADOR', 'SUPERADMINISTRADOR']:
                    return redirect('libros:lista')
                else:
                    return redirect('usuarios:perfil')
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})

@login_required
def logout_usuario(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('usuarios:login')

@login_required
def perfil_usuario(request):
    if request.method == 'POST':
        form = ActualizarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            usuario = form.save()
            Historial.registrar_cambio(
                usuario=request.user,
                tipo_entidad='USUARIO',
                tipo_accion='MODIFICACION',
                entidad_id=usuario.id,
                detalles='Actualización de perfil de usuario'
            )
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('usuarios:perfil')
    else:
        form = ActualizarPerfilForm(instance=request.user)

    # Solo mostrar préstamos activos para usuarios con rol CLIENTE
    context = {'form': form}
    if request.user.rol == 'CLIENTE':
        prestamos_activos = Prestamo.objects.filter(
            usuario=request.user,
            estado='APROBADO',
            fecha_devolucion_real__isnull=True
        ).order_by('-fecha_aprobacion')
        context['prestamos_activos'] = prestamos_activos

    return render(request, 'usuarios/perfil.html', context)

@login_required
def lista_usuarios(request):
    if not request.user.is_superadmin() and not request.user.is_admin():
        messages.error(request, 'No tienes permisos para ver esta página.')
        return redirect('usuarios:perfil')
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})

@login_required
def registrar_admin(request):
    if not request.user.is_superadmin() and not request.user.is_admin():
        messages.error(request, 'No tienes permisos para registrar administradores.')
        return redirect('usuarios:perfil')

    if request.method == 'POST':
        form = RegistroAdminForm(request.POST)
        if form.is_valid():
            admin = form.save()
            Historial.registrar_cambio(
                usuario=request.user,
                tipo_entidad='USUARIO',
                tipo_accion='CREACION',
                entidad_id=admin.id,
                detalles=f'Registro de nuevo administrador: {admin.username}'
            )
            messages.success(request, 'Administrador registrado exitosamente.')
            return redirect('usuarios:lista_usuarios')
    else:
        form = RegistroAdminForm()
    return render(request, 'usuarios/registrar_admin.html', {'form': form})