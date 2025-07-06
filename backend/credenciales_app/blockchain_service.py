# Archivo: D:\PS\backend\credenciales_app\blockchain_service.py
# --- VERSIÓN CON TU CAMBIO A 'errors="ignore"' ---

from web3 import Web3
from django.conf import settings
import json
import ipfshttpclient
import requests

class BlockchainService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_NETWORK_RPC_URL))
        if not self.w3.is_connected():
            raise ConnectionError("No se pudo conectar al nodo blockchain.")

        self.contract_address = settings.SMART_CONTRACT_ADDRESS
        self.contract_abi = settings.SMART_CONTRACT_ABI
        if not self.contract_address or not self.contract_abi:
            raise ValueError("Dirección o ABI del contrato no configurados en settings.py")

        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
        self.django_account = self.w3.eth.account.from_key(settings.DJANGO_WALLET_PRIVATE_KEY)
        self.w3.eth.default_account = self.django_account.address

        try:
           self.ipfs_client = ipfshttpclient.connect(settings.IPFS_API_MULTIADDR)
           print("Conectado a nodo IPFS local.")
        except Exception as e:
            print(f"Advertencia: No se pudo conectar al nodo IPFS local: {e}. Funcionalidad IPFS limitada.")
            self.ipfs_client = None

    def _upload_to_ipfs(self, data: dict) -> str:
        if self.ipfs_client:
            try:
                cid = self.ipfs_client.add_json(data)
                print(f"Metadatos subidos a IPFS local. CID recibido: {cid}")
                return cid
            except Exception as e:
                print(f"Error subiendo a IPFS local: {e}")
                raise
        else:
            raise ConnectionError("No hay cliente IPFS configurado (local o Pinata).")

    # ======================================================================
    #                 TU VERSIÓN DE EMITIR_CREDENCIAL
    # ======================================================================
    def emitir_credencial(self, direccion_alumno: str, datos_credencial: dict) -> dict:
        if not self.w3.is_address(direccion_alumno):
            raise ValueError("Dirección del alumno inválida.")

        metadata = {
            "name": f"Credencial para {datos_credencial.get('nombre_alumno', 'Estudiante')}",
            "description": f"Credencial digital emitida por la institución para el estudiante con ID {datos_credencial.get('id_estudiante', 'N/A')}.",
            "image": datos_credencial.get('imagen_url_ipfs', ''),
            "attributes": [
                {"trait_type": "ID Estudiante", "value": str(datos_credencial.get('id_estudiante', ''))},
                {"trait_type": "Programa", "value": str(datos_credencial.get('programa', ''))},
                {"trait_type": "Fecha Emision", "value": str(datos_credencial.get('fecha_emision', ''))},
            ]
        }
        token_cid = self._upload_to_ipfs(metadata)
        token_uri = token_cid

        nonce = self.w3.eth.get_transaction_count(self.django_account.address)
        tx_params = {
            'from': self.django_account.address,
            'nonce': nonce,
        }

        transaction = self.contract.functions.emitirCredencial(
            self.w3.to_checksum_address(direccion_alumno),
            token_uri
        ).build_transaction(tx_params)

        signed_tx = self.w3.eth.account.sign_transaction(transaction, private_key=settings.DJANGO_WALLET_PRIVATE_KEY)
        
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt.status == 1:
            try:
                # Cambiado a "ignore" (minúsculas) según tu especificación
                processed_logs = self.contract.events.CredencialEmitida().process_receipt(tx_receipt, errors="ignore")
                
                if processed_logs:
                    evento_args = processed_logs[0]['args']
                    token_id = evento_args['tokenId']
                    emitted_token_uri = evento_args['tokenURI']
                    
                    print(f"Credencial emitida y evento parseado! Token ID: {token_id}, URI: {emitted_token_uri}")
                    
                    return {
                        "success": True,
                        "tx_hash": tx_hash.hex(),
                        "token_id": token_id,
                        "token_uri": emitted_token_uri,
                        "block_number": tx_receipt.blockNumber
                    }
                else:
                    print(f"ADVERTENCIA: Transacción exitosa pero el evento 'CredencialEmitida' no fue encontrado en los logs. Hash: {tx_hash.hex()}")
                    return {
                        "success": True, 
                        "tx_hash": tx_hash.hex(), 
                        "message": "La credencial fue emitida, pero no se pudo leer el ID del token del evento."
                    }
            except Exception as e:
                print(f"ERROR al procesar el recibo de la transacción: {e}")
                return {
                    "success": True, 
                    "tx_hash": tx_hash.hex(), 
                    "message": f"La credencial fue emitida, pero ocurrió un error al leer el resultado: {e}"
                }
        else:
            raise Exception(f"La transacción para emitir la credencial falló. Hash: {tx_hash.hex()}")

    def verificar_credencial_por_id(self, token_id: int) -> dict:
        try:
            print(f"\n[DEBUG-VERIFICACION] Iniciando verificación para token ID: {token_id}")
            
            print("[DEBUG-VERIFICACION] Intentando llamar a la función 'ownerOf'...")
            owner = self.contract.functions.ownerOf(token_id).call()
            print(f"[DEBUG-VERIFICACION] Éxito. Dueño encontrado: {owner}")

            print("[DEBUG-VERIFICACION] Intentando llamar a la función 'tokenURI'...")
            uri = self.contract.functions.tokenURI(token_id).call()
            print(f"[DEBUG-VERIFICACION] Éxito. URI encontrada: {uri}")

            print("[DEBUG-VERIFICACION] Intentando descargar metadatos desde IPFS...")
            metadata = {}
            if self.ipfs_client and uri:
                try:
                    cid_to_fetch = uri.replace("ipfs://", "")
                    metadata_bytes = self.ipfs_client.cat(cid_to_fetch)
                    metadata_str = metadata_bytes.decode('utf-8')
                    print("[DEBUG-VERIFICACION] Contenido crudo de metadatos desde IPFS:", metadata_str)

                    metadata = json.loads(metadata_str)
                    if not isinstance(metadata, dict):
                        raise ValueError("El contenido decodificado desde IPFS no es un JSON dict.")

                    print("[DEBUG-VERIFICACION] Éxito. Metadatos descargados y parseados.")

                except json.JSONDecodeError as e:
                    print(f"[ERROR-IPFS] JSON inválido desde IPFS: {e}")
                    metadata = {}
                except Exception as e:
                    print(f"[ERROR-IPFS] Error general procesando metadatos desde IPFS: {e}")
                    metadata = {}
            else:
                print("[DEBUG-VERIFICACION] No hay cliente IPFS o no se encontró URI para descargar metadatos.")

            return {
                "token_id": token_id,
                "owner": owner,
                "token_uri_onchain": uri,
                "metadata": metadata,
                "valida": True
            }
        except Exception as e:
            print(f"\n[ERROR-VERIFICACION] Error específico durante la verificación del token ID {token_id}:")
            print(f"[ERROR-VERIFICACION] TIPO DE ERROR: {type(e).__name__}")
            print(f"[ERROR-VERIFICACION] MENSAJE: {e}\n")
            return { "token_id": token_id, "valida": False, "error": str(e) }

    def get_credenciales_de_alumno(self, direccion_alumno: str) -> list:
        if not self.w3.is_address(direccion_alumno):
            raise ValueError("Dirección del alumno inválida.")

        direccion_alumno_cs = self.w3.to_checksum_address(direccion_alumno)
        balance = self.contract.functions.balanceOf(direccion_alumno_cs).call()
        token_ids = []
        for i in range(balance):
            try:
                token_id = self.contract.functions.tokenOfOwnerByIndex(direccion_alumno_cs, i).call()
                token_ids.append(token_id)
            except Exception as e:
                print(f"Error obteniendo token en el índice {i} para {direccion_alumno_cs}: {e}")
        return token_ids