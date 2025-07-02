# credenciales_app/blockchain_service.py
from web3 import Web3
from django.conf import settings
import json
import ipfshttpclient # Para subir a IPFS local
# from pinatapy import PinataPy # Si usas Pinata

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
        # La cuenta que usará Django para firmar transacciones (el owner del contrato)
        self.django_account = self.w3.eth.account.from_key(settings.DJANGO_WALLET_PRIVATE_KEY)
        self.w3.eth.default_account = self.django_account.address # Opcional, pero puede simplificar algunas llamadas

        # Configuración IPFS
        # Opción 1: Nodo IPFS Local
        try:
            self.ipfs_client = ipfshttpclient.connect(settings.IPFS_API_MULTIADDR)
            print("Conectado a nodo IPFS local.")
        except Exception as e:
            print(f"Advertencia: No se pudo conectar al nodo IPFS local: {e}. Funcionalidad IPFS limitada.")
            self.ipfs_client = None

        # Opción 2: Pinata (descomentar y configurar PINATA_ en .env y settings.py)
        # if settings.PINATA_API_KEY and settings.PINATA_SECRET_API_KEY:
        #     self.pinata = PinataPy(settings.PINATA_API_KEY, settings.PINATA_SECRET_API_KEY)
        #     print("Configurado para usar Pinata.")
        # else:
        #     self.pinata = None
        #     print("Advertencia: Claves de Pinata no configuradas. Funcionalidad Pinata limitada.")


    def _upload_to_ipfs(self, data: dict) -> str:
        """Sube un diccionario JSON a IPFS y devuelve el CID."""
        json_data = json.dumps(data)
        # Usando IPFS local
        if self.ipfs_client:
            try:
                res = self.ipfs_client.add_json(json_data)
                print(f"Metadatos subidos a IPFS local. CID: {res}")
                return res # Este es el CID
            except Exception as e:
                print(f"Error subiendo a IPFS local: {e}")
                raise
        # Usando Pinata (descomentar si se usa)
        # elif self.pinata:
        #     try:
        #         # Pinata no tiene un add_json directo, subimos como archivo
        #         # Guardar temporalmente como archivo para subirlo
        #         temp_filename = "temp_metadata.json"
        #         with open(temp_filename, "w") as f:
        #             f.write(json_data)
        #         result = self.pinata.pin_file_to_ipfs(temp_filename)
        #         os.remove(temp_filename) # Limpiar archivo temporal
        #         cid = result['IpfsHash']
        #         print(f"Metadatos subidos a Pinata. CID: {cid}")
        #         return cid
        #     except Exception as e:
        #         print(f"Error subiendo a Pinata: {e}")
        #         raise
        else:
            raise ConnectionError("No hay cliente IPFS configurado (local o Pinata).")

    def emitir_credencial(self, direccion_alumno: str, datos_credencial: dict) -> dict:
        if not self.w3.is_address(direccion_alumno):
            raise ValueError("Dirección del alumno inválida.")

        # 1. Preparar metadatos y subirlos a IPFS
        #    Los datos_credencial podrían ser: {'nombre_alumno': 'Juan Perez', 'id_estudiante': '123', ...}
        metadata = {
            "name": f"Credencial para {datos_credencial.get('nombre_alumno', 'Estudiante')}",
            "description": f"Credencial digital emitida por la institución para el estudiante con ID {datos_credencial.get('id_estudiante', 'N/A')}.",
            "image": datos_credencial.get('imagen_url_ipfs', ''), # Opcional: "ipfs://CID_DE_LA_IMAGEN"
            "attributes": [
                {"trait_type": "ID Estudiante", "value": str(datos_credencial.get('id_estudiante', ''))},
                {"trait_type": "Programa", "value": str(datos_credencial.get('programa', ''))},
                {"trait_type": "Fecha Emision", "value": str(datos_credencial.get('fecha_emision', ''))},
                # ... más atributos
            ]
        }
        token_cid = self._upload_to_ipfs(metadata) # Esto devuelve el CID
        token_uri = token_cid # El Smart Contract espera solo el CID si baseURI es "ipfs://"

        # 2. Construir y enviar la transacción al Smart Contract
        nonce = self.w3.eth.get_transaction_count(self.django_account.address)
        tx_params = {
            'from': self.django_account.address,
            'nonce': nonce,
            # 'gas': 2000000, # Estimar o fijar gas (Hardhat lo maneja bien localmente)
            # 'gasPrice': self.w3.to_wei('50', 'gwei') # Ajustar según la red
        }

        # Estimar gas (opcional, Hardhat lo hace bien, pero útil para testnets)
        # gas_estimate = self.contract.functions.emitirCredencial(
        #     self.w3.to_checksum_address(direccion_alumno),
        #     token_uri
        # ).estimate_gas({'from': self.django_account.address})
        # tx_params['gas'] = gas_estimate

        transaction = self.contract.functions.emitirCredencial(
            self.w3.to_checksum_address(direccion_alumno), # Asegurar checksum
            token_uri
        ).build_transaction(tx_params)

        signed_tx = self.w3.eth.account.sign_transaction(transaction, private_key=settings.DJANGO_WALLET_PRIVATE_KEY)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt.status == 1:
            # Extraer el tokenId del evento emitido
            # Necesitas el ABI completo para decodificar logs
            event_abi = next(item for item in self.contract_abi if item['type'] == 'event' and item['name'] == 'CredencialEmitida')
            # Los topics[0] es la firma del evento, topics[1] es el primer indexed arg, etc.
            # O decodificar todos los logs si hay varios eventos
            logs = self.contract.events.CredencialEmitida().process_receipt(tx_receipt)
            if logs:
                token_id = logs[0]['args']['tokenId']
                emitted_token_uri = logs[0]['args']['tokenURI'] # Debería ser igual a token_uri
                print(f"Credencial emitida! Token ID: {token_id}, URI: {emitted_token_uri}")
                return {
                    "success": True,
                    "tx_hash": tx_hash.hex(),
                    "token_id": token_id,
                    "token_uri": emitted_token_uri,
                    "block_number": tx_receipt.blockNumber
                }
            else: # Fallback si el parseo del evento falla
                print(f"Transacción exitosa, pero no se pudo parsear el evento CredencialEmitida. Hash: {tx_hash.hex()}")
                return {"success": True, "tx_hash": tx_hash.hex(), "message": "Evento no parseado."}
        else:
            raise Exception(f"Error en la transacción de emisión: {tx_hash.hex()}")


    def verificar_credencial_por_id(self, token_id: int) -> dict:
        try:
            owner = self.contract.functions.ownerOf(token_id).call()
            uri = self.contract.functions.tokenURI(token_id).call()
            # Descargar metadatos de IPFS
            metadata = {}
            if self.ipfs_client and uri:
                try:
                    # Asume que uri es solo el CID. Si tiene 'ipfs://', quítalo.
                    cid_to_fetch = uri.replace("ipfs://", "")
                    metadata_bytes = self.ipfs_client.cat(cid_to_fetch)
                    metadata = json.loads(metadata_bytes.decode('utf-8'))
                except Exception as e:
                    print(f"Error descargando metadatos de IPFS para {uri}: {e}")
            elif settings.PINATA_GATEWAY_URL and uri: # Usar gateway de Pinata
                 import requests
                 cid_to_fetch = uri.replace("ipfs://", "")
                 gateway_url = f"{settings.PINATA_GATEWAY_URL.rstrip('/')}/{cid_to_fetch}"
                 response = requests.get(gateway_url)
                 if response.status_code == 200:
                     metadata = response.json()
                 else:
                     print(f"Error descargando desde gateway Pinata ({gateway_url}): {response.status_code}")


            return {
                "token_id": token_id,
                "owner": owner,
                "token_uri_onchain": uri, # El CID
                "metadata": metadata, # Metadatos de IPFS
                "valida": True # El token existe
            }
        except Exception as e: # web3.exceptions.ContractLogicError si el token no existe
            print(f"Error verificando token ID {token_id}: {e}")
            return {"token_id": token_id, "valida": False, "error": str(e)}

    def get_credenciales_de_alumno(self, direccion_alumno: str) -> list:
        """Obtiene todos los token IDs de credenciales pertenecientes a un alumno."""
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