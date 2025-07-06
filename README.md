Sistema de Credenciales Digitales en Blockchain
Este proyecto es una aplicación full-stack que permite a una institución educativa emitir, gestionar y verificar credenciales estudiantiles digitales como Tokens No Fungibles (NFTs) en una blockchain compatible con Ethereum.

El sistema se compone de dos partes principales:

1-Backend (Django): Una API REST robusta que gestiona la lógica de negocio, se comunica con la blockchain y sirve como panel administrativo.

2-Blockchain (Hardhat): Un Smart Contract de tipo Soulbound (NFT no transferible) que define la lógica de las credenciales en la cadena de bloques.

Características Principales
-Emisión de Credenciales: La institución puede emitir credenciales únicas a las billeteras de los alumnos.

-Verificación Descentralizada: Cualquiera puede verificar la autenticidad de una credencial consultando el Smart Contract, sin necesidad de intermediarios.

-Inmutabilidad y Seguridad: Las credenciales, una vez emitidas, son seguras e inmutables gracias a la tecnología blockchain.

-Metadatos Descentralizados: La información detallada de cada credencial (nombre del alumno, programa, fechas) se almacena en IPFS para garantizar la descentralización y la disponibilidad.

-Tokens Soulbound: Las credenciales están diseñadas para no ser transferibles, vinculando la identidad digital directamente al alumno.

Arquitectura y Tecnologías Utilizadas
Backend:
-Framework: Django & Django REST Framework

-Lenguaje: Python

-Comunicación Blockchain: Web3.py

-Base de Datos: SQLite (desarrollo), compatible con PostgreSQL (producción).

Blockchain:
-Framework de Desarrollo: Hardhat

-Lenguaje del Smart Contract: Solidity

-Estándar de Token: ERC-721 (modificado para ser no transferible).

Almacenamiento de Metadatos:
-IPFS (InterPlanetary File System): A través de un nodo local (IPFS Desktop) o un servicio de pinning como Pinata.

Entorno de Desarrollo:

-Python: venv para la gestión de dependencias del backend.

-JavaScript/Node.js: npm para la gestión de dependencias de Hardhat.

Requisitos Previos
Antes de comenzar, asegúrate de tener instalado lo siguiente:

Node.js (versión LTS recomendada)

Python (versión 3.8 o superior)

IPFS Desktop (o acceso a un nodo IPFS)

Guía de Instalación y Ejecución Local
Sigue estos pasos para poner en marcha el proyecto en tu máquina local.

1. Clonar el Repositorio: git clone <URL_DEL_REPOSITORIO>

2. Configurar el Entorno de Blockchain (Hardhat)
Navega a la carpeta de blockchain e instala las dependencias de Node.js.
-cd blockchain
-npm install

3. Configurar el Entorno del Backend (Django)
Navega a la carpeta del backend, crea un entorno virtual de Python y activa las dependencias.

cd ../backend  # Sube un nivel y entra a backend
python -m venv venv

# Activar el entorno virtual
# En Windows:
.\venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar las dependencias de Python
pip install -r requirements.txt

4. Configurar las Variables de Entorno
En la carpeta backend/, crea un archivo llamado .env a partir del ejemplo env.example (si lo tienes) o créalo desde cero con el siguiente contenido:
# backend/.env

# Configuración de Django
SECRET_KEY="tu-clave-secreta-aqui"
DEBUG=True

# Configuración de Blockchain (para nodo local de Hardhat)
BLOCKCHAIN_NETWORK_RPC_URL="http://127.0.0.1:8545"
DJANGO_WALLET_PRIVATE_KEY="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

# Configuración IPFS (nodo local)
IPFS_API_MULTIADDR="/ip4/127.0.0.1/tcp/5001"
IPFS_GATEWAY_URL="http://127.0.0.1:8080/ipfs/"

Nota: La DJANGO_WALLET_PRIVATE_KEY es la clave privada de la primera cuenta que Hardhat genera.

5. Ejecutar el Sistema (Orden de Encendido)
Debes tener 3 o 4 terminales abiertas.

Terminal 1: Iniciar el Nodo Blockchain
# Desde la carpeta /blockchain
npx hardhat node

Terminal 2: Iniciar el Nodo IPFS

Abre la aplicación IPFS Desktop y espera a que se conecte.

Terminal 3: Desplegar el Smart Contract

# Desde la carpeta /blockchain
npx hardhat run scripts/deploy.js --network localhost

Este comando despliega el contrato y crea los archivos de configuración para que Django pueda comunicarse con él.

Terminal 4: Iniciar el Servidor Django

# Desde la carpeta /backend y con el venv activado
python manage.py migrate
python manage.py runserver

Tu API ahora estará disponible en http://127.0.0.1:8000/.

Endpoints de la API
POST /api/credenciales/emitir/

Emite una nueva credencial.

Body (JSON):
{
    "direccion_alumno": "0x...",
    "datos_credencial": {
        "nombre_alumno": "...",
        "id_estudiante": "...",
        "programa": "...",
        "fecha_emision": "YYYY-MM-DD"
    }
}
GET /api/credenciales/verificar/<int:token_id>/

Verifica los detalles de una credencial existente por su ID.

GET /api/credenciales/alumno/<str:direccion_alumno>/

Lista todas las credenciales pertenecientes a una dirección de alumno.
jkj