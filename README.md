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
Resumen del proyecto:
Arquitectura de la Infraestructura Blockchain (Hyperledger Fabric)
Este documento describe los componentes fundamentales, el flujo de datos y la estructura del ledger de la red blockchain implementada para el sistema de credenciales digitales.
1. Visión General
La plataforma seleccionada es Hyperledger Fabric v2.5, un framework de la Linux Foundation diseñado para soluciones empresariales. Se implementó una red privada y permisionada, lo que garantiza que solo las entidades autorizadas puedan participar, asegurando un alto grado de control, seguridad y privacidad.
La topología de la red de prueba consiste en:
2 Organizaciones: Org1 (Emisora) y Org2 (Verificadora).
1 Servicio de Ordenamiento: Para el consenso de transacciones.
1 Canal de Comunicación: Un ledger privado llamado mychannel donde interactúan las organizaciones.
2. Componentes Principales
La red está compuesta por varios tipos de nodos, cada uno con una función específica, que se ejecutan como contenedores Docker independientes.
2.1. Nodos Peer (Pares)
Función: Son los nodos fundamentales de la red, mantenidos por cada organización.
Responsabilidades:
Almacenar el Ledger: Cada peer mantiene una copia completa y sincronizada del libro de contabilidad del canal.
Ejecutar el Chaincode: Simulan las transacciones y validan si cumplen con la lógica de negocio definida en el smart contract.
Endosar Transacciones: Firman criptográficamente las propuestas de transacción válidas antes de que sean enviadas para su ordenamiento.
2.2. Nodo Orderer (Servicio de Ordenamiento)
Función: Actúa como el servicio central de consenso de la red.
Responsabilidades:
Recibir Transacciones Endosadas: Recibe las transacciones validadas de los clientes.
Ordenar y Empaquetar: Ordena las transacciones cronológicamente y las empaqueta en bloques inmutables.
Distribuir Bloques: Entrega los nuevos bloques a todos los peers del canal para que actualicen sus ledgers.
2.3. Autoridad de Certificación (CA)
Función: Es el servicio de gestión de identidades de cada organización.
Responsabilidades:
Emitir Identidades: Genera los certificados digitales (X.509) que sirven como "pasaportes" para todos los participantes (peers, orderers, usuarios, aplicaciones).
Gestionar el MSP (Membership Service Provider): Provee la infraestructura para validar que una firma pertenece a una identidad válida y autorizada dentro de la red.
3. El Ledger: Almacenamiento de Datos
El ledger de Fabric es la "fuente de la verdad" y se compone de dos partes distintas pero relacionadas.
3.1. La Cadena de Bloques (Blockchain)
¿Qué es? Es un historial de transacciones, estructurado como una cadena de bloques enlazados criptográficamente. Es un registro de solo adición (append-only).
¿Qué almacena? Cada bloque contiene un conjunto de transacciones, incluyendo los argumentos de la función llamada y los read-write sets (qué datos se leyeron y qué nuevos datos se escribieron).
Propósito: Garantizar la inmutabilidad y trazabilidad. Permite una auditoría completa de la historia de cualquier activo.
Ubicación Física: Se almacena en el sistema de archivos del contenedor del peer.
3.2. El Estado Mundial (World State)
¿Qué es? Es una base de datos que representa el estado actual y final de todos los activos en el ledger. Es una "fotografía" del presente.
¿Qué almacena? Contiene pares clave-valor. La clave es el ID del activo (ej. "credencial01") y el valor son sus atributos actuales (ej. {"Owner":"Marcelo", "Programa":"Ing. Blockchain", ...}).
Propósito: Permitir consultas de lectura (query) rápidas y eficientes. En lugar de recorrer toda la historia, el peer consulta directamente esta base de datos.
Ubicación Física: En nuestra implementación, se utiliza CouchDB. Los datos residen en un contenedor Docker de base de datos separado, vinculado a cada peer, y son accesibles a través de su API o interfaz web.
4. Chaincode (Smart Contract)
¿Qué es? Es el programa que encapsula la lógica de negocio y las reglas de la aplicación. En nuestro caso, está escrito en Go.
¿Para qué sirve?
Define la estructura de datos de los activos (ej. la estructura de una Credencial).
Implementa las funciones que pueden interactuar con el ledger (ej. CreateAsset, ReadAsset).
Contiene la lógica de validación que determina si una transacción es válida o no.
Ciclo de Vida: El chaincode es instalado en los peers y luego desplegado (cometido) en un canal para ser activado.
5. Canales
¿Qué es? Un mecanismo que permite crear un ledger privado y aislado entre un subconjunto de miembros de la red.
Propósito: Proporcionar confidencialidad. Las transacciones y los datos de un canal solo son visibles para las organizaciones que son miembros de ese canal. Cada canal tiene su propio ledger y su propio chaincode instanciado. En este proyecto, se utiliza un único canal (mychannel) que incluye a todas las organizaciones.
