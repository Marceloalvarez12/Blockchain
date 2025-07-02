# credenciales_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .blockchain_service import BlockchainService
from django.conf import settings # Para acceder a IPFS_GATEWAY_URL

class EmitirCredencialView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            direccion_alumno = request.data.get('direccion_alumno')
            # datos_credencial contendrá la info para los metadatos
            datos_credencial = request.data.get('datos_credencial', {}) # ej: {'nombre_alumno': 'Luis', 'id_estudiante': 'S123', ...}

            if not direccion_alumno or not datos_credencial:
                return Response(
                    {"error": "direccion_alumno y datos_credencial son requeridos."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            service = BlockchainService()
            resultado = service.emitir_credencial(direccion_alumno, datos_credencial)
            return Response(resultado, status=status.HTTP_201_CREATED)
        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectionError as ce:
            return Response({"error": f"Error de conexión: {ce}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            # Loggear el error real (e)
            print(f"Error inesperado en EmitirCredencialView: {e}")
            return Response({"error": f"Error interno del servidor: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerificarCredencialView(APIView):
    def get(self, request, token_id, *args, **kwargs):
        try:
            service = BlockchainService()
            resultado = service.verificar_credencial_por_id(int(token_id))
            if resultado.get("valida"):
                # Si quieres que la URL de la imagen sea accesible directamente desde el frontend
                if 'metadata' in resultado and 'image' in resultado['metadata'] and resultado['metadata']['image'].startswith('ipfs://'):
                    cid_imagen = resultado['metadata']['image'].replace('ipfs://', '')
                    # Determina qué gateway usar (Pinata o local)
                    ipfs_gateway = getattr(settings, 'PINATA_GATEWAY_URL', settings.IPFS_GATEWAY_URL)
                    if ipfs_gateway:
                       resultado['metadata']['image_http_url'] = f"{ipfs_gateway.rstrip('/')}/{cid_imagen}"

                return Response(resultado, status=status.HTTP_200_OK)
            else:
                return Response(resultado, status=status.HTTP_404_NOT_FOUND)
        except ConnectionError as ce:
             return Response({"error": f"Error de conexión: {ce}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            print(f"Error inesperado en VerificarCredencialView: {e}")
            return Response({"error": "Error interno del servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CredencialesPorAlumnoView(APIView):
    def get(self, request, direccion_alumno, *args, **kwargs):
        try:
            service = BlockchainService()
            token_ids = service.get_credenciales_de_alumno(direccion_alumno)
            credenciales_info = []
            for token_id in token_ids:
                info = service.verificar_credencial_por_id(token_id) # Reutilizamos para obtener detalles
                if info.get("valida"):
                     if 'metadata' in info and 'image' in info['metadata'] and info['metadata']['image'].startswith('ipfs://'):
                        cid_imagen = info['metadata']['image'].replace('ipfs://', '')
                        ipfs_gateway = getattr(settings, 'PINATA_GATEWAY_URL', settings.IPFS_GATEWAY_URL)
                        if ipfs_gateway:
                            info['metadata']['image_http_url'] = f"{ipfs_gateway.rstrip('/')}/{cid_imagen}"
                     credenciales_info.append(info)

            return Response({"direccion_alumno": direccion_alumno, "credenciales": credenciales_info}, status=status.HTTP_200_OK)
        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectionError as ce:
             return Response({"error": f"Error de conexión: {ce}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            print(f"Error inesperado en CredencialesPorAlumnoView: {e}")
            return Response({"error": "Error interno del servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)