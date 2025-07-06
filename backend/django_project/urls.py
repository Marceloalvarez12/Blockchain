# django_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/credenciales/', include('credenciales_app.urls')), # Tu app
]