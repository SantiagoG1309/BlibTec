from django.urls import path
from . import views

app_name = 'prestamos'

urlpatterns = [
    path('', views.lista_prestamos, name='lista_prestamos'),
    path('<int:prestamo_id>/', views.detalle_prestamo, name='detalle_prestamo'),
    path('solicitar/<int:libro_id>/', views.solicitar_prestamo, name='solicitar_prestamo'),
    path('<int:prestamo_id>/aprobar/', views.aprobar_prestamo, name='aprobar_prestamo'),
    path('<int:prestamo_id>/rechazar/', views.rechazar_prestamo, name='rechazar_prestamo'),
    path('<int:prestamo_id>/devolver/', views.devolver_prestamo, name='devolver_prestamo'),
    path('mis-prestamos/', views.mis_prestamos, name='mis_prestamos'),
    path('historial-prestamos/', views.cliente_historial_prestamos, name='cliente_historial_prestamos'),
]