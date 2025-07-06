# Archivo: credenciales_app/admin.py
# --- ADAPTADO A TUS MODELOS ---

from django.contrib import admin, messages
from .models import Alumno, CredencialBlockchain
from .blockchain_service import BlockchainService
from datetime import datetime

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    # Asumo que en tu modelo Alumno no tienes el campo 'direccion_wallet',
    # así que lo quito de aquí. Si lo tienes, puedes volver a añadirlo.
    list_display = ('nombre_completo', 'id_estudiante_institucional', 'programa_academico', 'user')
    search_fields = ('nombre_completo', 'id_estudiante_institucional')

@admin.register(CredencialBlockchain)
class CredencialBlockchainAdmin(admin.ModelAdmin):
    list_display = ('token_id', 'alumno', 'estado', 'tx_hash_emision', 'fecha_creacion')
    list_filter = ('estado',)
    search_fields = ('alumno__nombre_completo',)
    
    # Hacemos que los campos que se llenan automáticamente sean de solo lectura en el admin
    readonly_fields = (
        'token_id', 
        'tx_hash_emision', 
        'tx_hash_revocacion',
        'metadata_json',
        'metadata_cid',
        'estado', 
        'fecha_creacion',
        'fecha_ultima_actualizacion'
    )
    
    # Campos que se mostrarán en el formulario de creación.
    # Solo necesitamos que el admin seleccione el alumno y la wallet.
    # El resto se rellena solo.
    add_fieldsets = (
        (None, {
            'fields': ('alumno', 'direccion_wallet_alumno')
        }),
    )

    # Para que add_fieldsets funcione en el formulario de creación
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    # ¡¡AQUÍ ESTÁ LA LÓGICA CLAVE!!
    # Sobrescribimos el método que se ejecuta al guardar.
    def save_model(self, request, obj, form, change):
        # 'obj' es la instancia de CredencialBlockchain que se está guardando
        
        # Solo ejecutamos la lógica de emisión si es un objeto NUEVO
        # y si su estado es PENDIENTE
        if not change and obj.estado == 'PENDIENTE':
            try:
                # 1. Preparamos los datos para el servicio, usando tus modelos
                direccion_alumno_wallet = obj.direccion_wallet_alumno
                datos_credencial = {
                    'nombre_alumno': obj.alumno.nombre_completo,
                    'id_estudiante': obj.alumno.id_estudiante_institucional,
                    'programa': obj.alumno.programa_academico,
                    'fecha_emision': datetime.now().strftime("%Y-%m-%d")
                }

                # 2. Llamamos a nuestro servicio de blockchain
                print(f"Iniciando emisión de credencial para {obj.alumno.nombre_completo} desde el Admin.")
                service = BlockchainService()
                resultado = service.emitir_credencial(direccion_alumno_wallet, datos_credencial)

                # 3. Actualizamos el objeto con los resultados
                if resultado.get('success'):
                    obj.token_id = resultado.get('token_id')
                    obj.tx_hash_emision = resultado.get('tx_hash')
                    obj.metadata_cid = resultado.get('token_uri')
                    # Guardamos una copia del JSON de metadatos
                    obj.metadata_json = {
                        "name": datos_credencial['nombre_alumno'],
                        "attributes": [
                            {"trait_type": "ID Estudiante", "value": datos_credencial['id_estudiante']},
                            {"trait_type": "Programa", "value": datos_credencial['programa']},
                            {"trait_type": "Fecha Emision", "value": datos_credencial['fecha_emision']},
                        ]
                    }
                    obj.estado = 'EMITIDA'
                    messages.success(request, f"¡Éxito! Credencial emitida. Token ID: {obj.token_id}")
                else:
                    obj.estado = 'ERROR'
                    obj.notas_error = resultado.get('message', 'Error desconocido durante la emisión.') # Asumo que tienes un campo notas_error
                    messages.error(request, f"Error al emitir credencial: {obj.notas_error}")

            except Exception as e:
                # Si ocurre cualquier excepción, la guardamos
                print(f"ERROR grave durante la emisión desde el Admin: {e}")
                obj.estado = 'ERROR'
                # Necesitas añadir un campo 'notas_error = models.TextField(null=True, blank=True)'
                # a tu modelo CredencialBlockchain para que esto funcione.
                # obj.notas_error = str(e) 
                messages.error(request, f"Error grave al emitir credencial: {e}")
        
        # 4. Finalmente, guardamos el objeto en la base de datos (con los nuevos datos)
        super().save_model(request, obj, form, change)