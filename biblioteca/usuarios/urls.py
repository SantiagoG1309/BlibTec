from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('lista/', views.lista_usuarios, name='lista_usuarios'),
    path('registrar-admin/', views.registrar_admin, name='registrar_admin'),
]