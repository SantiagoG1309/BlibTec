from django.urls import path
from . import views

app_name = 'libros'

urlpatterns = [
    path('', views.lista_libros, name='lista'),
    path('buscar/', views.buscar_libros, name='buscar'),
    path('<int:libro_id>/', views.detalle_libro, name='detalle'),
    path('gestionar/crear/', views.gestionar_libro, name='gestionar_crear'),
    path('gestionar/<int:libro_id>/', views.gestionar_libro, name='gestionar'),
]