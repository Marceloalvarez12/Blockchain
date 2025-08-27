# Sistema de Credenciales Digitales con Hyperledger Fabric

## 1. Resumen

Este documento describe la arquitectura, instalación y operación de una red blockchain privada para la gestión de credenciales digitales. La implementación se basa en **Hyperledger Fabric v2.5** y sigue una planificación de proyecto orientada a un entorno empresarial.

La red está compuesta por dos organizaciones (una emisora y una verificadora) que interactúan a través de un canal de comunicación privado. La lógica de negocio está encapsulada en un Smart Contract (Chaincode) escrito en Go.

---

## 2. Requisitos del Entorno de Desarrollo

Para replicar este entorno en un sistema **Windows**, es necesario tener instalado el siguiente software:

-   **Docker Desktop (v4+):** Configurado con el backend **WSL 2**.
-   **Go (v1.18+):** El lenguaje del chaincode.
-   **Node.js (v16+ LTS):** Para herramientas de Fabric.
-   **Git (v2.28+):** Para descargar los ejemplos y proveer una terminal Bash.

---

## 3. Guía de Instalación y Despliegue

La siguiente secuencia de pasos debe ejecutarse para construir la red desde un entorno limpio.

### 3.1. Descarga de Activos de Fabric

1.  **Crear Directorio de Proyecto:**
    En una terminal **PowerShell**, crea un directorio en una ruta corta (ej. `C:\fabric-project`).
    ```powershell
    mkdir C:\fabric-project
    cd C:\fabric-project
    ```

2.  **Obtener Script de Instalación:**
    Descarga el script oficial.
    ```powershell
    Invoke-WebRequest -Uri https://raw.githubusercontent.com/hyperledger/fabric/main/scripts/install-fabric.sh -OutFile install-fabric.sh
    ```

3.  **Ejecutar Script de Instalación:**
    Este script debe ser ejecutado en una terminal **Git Bash**.
    ```bash
    ./install-fabric.sh docker samples binary
    ```
    Este comando descargará las imágenes de Docker, los binarios de Fabric (`peer`, `orderer`, etc.) y el repositorio `fabric-samples`.

### 3.2. Configuración Permanente del Entorno

Para que los binarios de Fabric sean accesibles desde cualquier terminal, su ruta debe ser añadida a las variables de entorno del sistema.

1.  **Añadir al PATH del Sistema:**
    -   Abre las "Variables de entorno del sistema" en Windows.
    -   En "Variables del sistema", edita la variable `Path`.
    -   Añade una nueva entrada con la ruta absoluta: `C:\fabric-project\fabric-samples\bin`

2.  **Reiniciar el Sistema:** Es **obligatorio** reiniciar la computadora para que los cambios en el PATH se apliquen a todas las terminales y a Docker Desktop.

### 3.3. Levantamiento de la Red Blockchain

Estos comandos deben ejecutarse en una terminal **PowerShell** dentro de VS Code, después de reiniciar el sistema.

1.  **Verificar Entorno Post-Reinicio:**
    -   Asegúrate de que Docker Desktop esté corriendo.
    -   Verifica que los binarios son accesibles:
        ```powershell
        peer.exe version
        ```

2.  **Navegar al Directorio de la Red:**
    ```powershell
    cd C:\fabric-project\fabric-samples\test-network
    ```

3.  **Iniciar la Red y el Canal:**
    ```powershell
    # Limpia cualquier residuo de ejecuciones anteriores
    .\network.sh down -v
    
    # Levanta la red, crea el canal 'mychannel', usa CAs y CouchDB
    .\network.sh up createChannel -ca -s couchdb
    ```
    Espera a que finalice con el mensaje `========= All GOOD, Test Network is up and running =========`.

4.  **Desplegar el Chaincode:**
    ```powershell
    .\network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-go -ccl go
    ```
    Espera a que finalice con el mensaje `========= Chaincode is successfully deployed on channel 'mychannel' ===========`.

---

## 4. Guía de Operación (Interacción con la Red)

Se recomienda usar una terminal **Git Bash** para la interacción, ya que maneja los argumentos JSON de forma más consistente.

### 4.1. Configuración de Identidad de Cliente

Antes de interactuar, es necesario adoptar la identidad de un miembro de la red. Cada vez que se abra una nueva terminal, ejecuta el siguiente bloque:

```bash
# Navegar al directorio de trabajo (si es necesario)
cd /c/fabric-project/fabric-samples/test-network

# Exportar las variables de entorno para el Admin de Org1
export PATH=${PWD}/../../bin:$PATH
export FABRIC_CFG_PATH=${PWD}/../config/
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051
```

### 4.2. Comandos Principales

#### Emitir una Nueva Credencial (Invoke)

Este comando **escribe** una nueva transacción en el ledger.

```bash
peer chaincode invoke \
    -o localhost:7050 \
    --ordererTLSHostnameOverride orderer.example.com \
    --tls \
    --cafile "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" \
    -C mychannel \
    -n basic \
    --peerAddresses localhost:7051 --tlsRootCertFiles "${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt" \
    --peerAddresses localhost:9051 --tlsRootCertFiles "${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt" \
    -c '{"function":"CreateAsset","Args":["credencial01", "Azul", "1", "Marcelo", "2024"]}'
```
**Respuesta esperada:** `Chaincode invoke successful. result: status:200`

#### Verificar una Credencial (Query)

Este comando **lee** el estado actual de un activo en el ledger sin generar una nueva transacción.

```bash
peer chaincode query -C mychannel -n basic -c '{"Args":["ReadAsset","credencial01"]}'.
```

# API Gateway para la Red de Credenciales Hyperledger Fabric

Este proyecto es un servicio intermedio (API Gateway) construido con **Node.js y Express**. Su única responsabilidad es actuar como un "traductor" seguro entre el mundo web (peticiones HTTP) y la red blockchain de Hyperledger Fabric.

Abstrae la complejidad del SDK de Fabric, exponiendo la funcionalidad del chaincode a través de endpoints RESTful simples.

## Arquitectura

```mermaid
graph TD
    A[Cualquier Cliente HTTP<br/>(ej. Backend de Django)] -->|POST /invoke<br/>GET /query| B{API Gateway (Este Proyecto)};
    B -->|Usa el SDK de Fabric| C(Red Hyperledger Fabric);
```

## Requisitos Previos

-   [Node.js](https://nodejs.org/) (v16+ LTS)
-   Una red Hyperledger Fabric `test-network` corriendo.
-   Archivos de conexión (`connection-org1.json`) y una `wallet` con la identidad `appUser` generada.

## Instalación

1.  **Clonar el repositorio y navegar a la carpeta:**
    ```bash
    # Asume que ya estás dentro del proyecto principal
    cd fabric-api-gateway
    ```

2.  **Instalar dependencias:**
    ```bash
    npm install
    ```

3.  **Configurar la conexión:**
    Asegúrate de que los siguientes archivos estén presentes en la raíz de este proyecto:
    -   `connection-org1.json`: El perfil de conexión de la Org1.
    -   `wallet/`: Una carpeta que contiene la identidad `appUser` previamente generada.

## Ejecución

Para iniciar el servidor de la API, ejecuta:
```bash
node api.js
```
El servidor se iniciará y escuchará peticiones en `http://localhost:3000`.

---

## Documentación de la API

La API expone dos endpoints principales para interactuar con el chaincode.

### 1. Invocar una Transacción (Escritura)

Este endpoint se utiliza para ejecutar funciones del chaincode que modifican el estado del ledger (ej. `CreateAsset`).

-   **URL:** `/invoke`
-   **Método:** `POST`
-   **Cuerpo (Body):** `JSON`
    -   `func` (string, requerido): El nombre de la función del chaincode a invocar.
    -   `args` (array de strings, requerido): Un array con los argumentos para la función.

-   **Ejemplo de Petición (para `CreateAsset`):**
    ```http
    POST /invoke HTTP/1.1
    Host: localhost:3000
    Content-Type: application/json

    {
        "func": "CreateAsset",
        "args": [
            "credencial-api-01",
            "Ingenieria en Sistemas",
            "2024001",
            "Marcelo Alvarez",
            "2025"
        ]
    }
    ```

-   **Respuesta de Éxito (Código `201 Created`):**
    ```json
    {
        "success": true,
        "message": "Transacción \"CreateAsset\" enviada exitosamente."
    }
    ```

-   **Respuesta de Error (Código `400` o `500`):**
    ```json
    {
        "error": "Descripción del error ocurrido en el SDK o en el chaincode."
    }
    ```

### 2. Consultar el Ledger (Lectura)

Este endpoint se utiliza para ejecutar funciones del chaincode de solo lectura (ej. `ReadAsset`).

-   **URL:** `/query/:func/:args`
-   **Método:** `GET`
-   **Parámetros de URL:**
    -   `:func` (string, requerido): El nombre de la función del chaincode a consultar.
    -   `:args` (string, requerido): El argumento para la función (actualmente solo soporta un argumento).

-   **Ejemplo de Petición (para `ReadAsset`):**
    ```http
    GET /query/ReadAsset/credencial-api-01 HTTP/1.1
    Host: localhost:3000
    ```

-   **Respuesta de Éxito (Código `200 OK`):**
    La respuesta es el objeto JSON devuelto directamente por el chaincode.
    ```json
    {
        "ID": "credencial-api-01",
        "Color": "Ingenieria en Sistemas",
        "Size": 2024001,
        "Owner": "Marcelo Alvarez",
        "AppraisedValue": 2025
    }
    ```

-   **Respuesta de Error (Código `404` o `500`):**
    ```json
    {
        "error": "Descripción del error, ej: el activo credencial-api-01 no existe."
    }
    ```

---

## Notas de Desarrollo

-   **Identidad:** La API utiliza una identidad fija (`appUser`) para todas las interacciones con la blockchain. La gestión de permisos de los usuarios finales debe ser manejada por el backend que consume esta API (ej. Django).
-   **Canal y Chaincode:** Los nombres del canal (`mychannel`) y del chaincode (`basic`) están definidos directamente en el código (`api.js`). Si cambian en la red, deben ser actualizados aquí.
-   **Logs:** La API imprime en la consola cada transacción que procesa, lo que es útil para la depuración.


