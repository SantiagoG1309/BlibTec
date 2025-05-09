from django.urls import path
from . import views

app_name = 'libros'

urlpatterns = [
    path('', views.lista_libros, name='lista'),
    path('buscar/', views.buscar_libros, name='buscar'),
    path('<int:libro_id>/', views.detalle_libro, name='detalle'),
    path('gestionar/crear/', views.gestionar_libro, name='gestionar_crear'),
    path('gestionar/<int:libro_id>/', views.gestionar_libro, name='gestionar'),
    path('categorias/', views.gestionar_categorias, name='gestionar_categorias'),
    path('categorias/<int:categoria_id>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:categoria_id>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),
]