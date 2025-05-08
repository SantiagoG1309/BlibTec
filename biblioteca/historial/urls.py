from django.urls import path
from . import views

app_name = 'historial'

urlpatterns = [
    path('', views.lista_historial, name='lista_historial'),
    path('<str:tipo_entidad>/<int:entidad_id>/', views.historial_por_entidad, name='historial_por_entidad'),
]