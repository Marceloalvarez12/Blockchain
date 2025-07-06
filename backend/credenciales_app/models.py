# Archivo: D:\PS\backend\credenciales_app\models.py
# --- CORREGIDO PARA PERMITIR VALORES NULOS ---

from django.db import models
from django.contrib.auth.models import User

class Alumno(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_completo = models.CharField(max_length=255)
    id_estudiante_institucional = models.CharField(max_length=50, unique=True)
    programa_academico = models.CharField(max_length=150)
    # ... otros campos que necesites sobre el alumno

    def __str__(self):
        return self.nombre_completo

class CredencialBlockchain(models.Model):
    ESTADOS = (
        ('PENDIENTE', 'Pendiente de emisión'),
        ('EMITIDA', 'Emitida en Blockchain'), # Cambiado de ACTIVA a EMITIDA para coincidir con el admin.py
        ('REVOCADA', 'Revocada'),
        ('ERROR', 'Error de emisión'),
    )

    token_id = models.PositiveIntegerField(unique=True, null=True, blank=True, help_text="El ID del token NFT en la blockchain")
    
    # Relación con el alumno
    alumno = models.ForeignKey(Alumno, on_delete=models.PROTECT, related_name='credenciales')
    
    direccion_wallet_alumno = models.CharField(max_length=42, help_text="Dirección de la wallet a la que se emitió")
    tx_hash_emision = models.CharField(max_length=66, unique=True, null=True, blank=True, help_text="Hash de la transacción de emisión")
    tx_hash_revocacion = models.CharField(max_length=66, unique=True, null=True, blank=True, help_text="Hash de la transacción de revocación")
    
    # ======================================================================
    #                      ¡AQUÍ ESTÁ LA CORRECCIÓN!
    #        Añadimos null=True y blank=True para permitir valores vacíos
    # ======================================================================
    metadata_json = models.JSONField(null=True, blank=True, help_text="Copia del JSON de metadatos subido a IPFS")
    # ======================================================================
    
    metadata_cid = models.CharField(max_length=100, help_text="CID del archivo de metadatos en IPFS")
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)

    # (Opcional pero recomendado) Campo para guardar el mensaje de error
    notas_error = models.TextField(null=True, blank=True, help_text="Detalles del error si la emisión falla")

    def __str__(self):
        return f"Credencial #{self.token_id} para {self.alumno.nombre_completo}"

    class Meta:
        verbose_name = "Credencial Blockchain"
        verbose_name_plural = "Credenciales Blockchain"