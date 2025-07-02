# credenciales_app/urls.py
from django.urls import path
from .views import EmitirCredencialView, VerificarCredencialView, CredencialesPorAlumnoView

urlpatterns = [
    path('emitir/', EmitirCredencialView.as_view(), name='emitir_credencial'),
    path('verificar/<int:token_id>/', VerificarCredencialView.as_view(), name='verificar_credencial'),
    path('alumno/<str:direccion_alumno>/', CredencialesPorAlumnoView.as_view(), name='credenciales_por_alumno'),
]