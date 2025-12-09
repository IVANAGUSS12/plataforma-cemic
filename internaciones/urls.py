from django.urls import path
from . import views

urlpatterns = [
    path('', views.censo, name='internaciones_censo'),
    path('ver/<int:pk>/', views.ver_internacion, name='internaciones_ver_internacion'),
    path('cobertura/<str:cobertura_nombre>/', views.censo_cobertura, name='internaciones_cobertura'),
    path('hc/', views.hc_lista_pacientes, name='hc_lista_pacientes'),
    path('hc/<int:pk>/', views.hc_detalle_paciente, name='hc_detalle_paciente'),
]
