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
peer chaincode query -C mychannel -n basic -c '{"Args":["ReadAsset","credencial01"]}'

Resumen del proyecto:
¡Perfecto! Centrémonos exclusivamente en la "Caja Fuerte Maestra" y sus componentes internos.

Aquí tienes un resumen detallado de la parte de **blockchain (Hyperledger Fabric)**, explicando qué es cada pieza, para qué sirve y dónde se guardan los datos.

---

### **Resumen Conceptual de la Infraestructura Blockchain**

Imagina tu sistema de credenciales como una **notaría digital de máxima seguridad**, compartida entre varias instituciones de confianza (como la UTN y empresas).

#### **1. La Red Hyperledger Fabric (La Notaría en sí)**
*   **¿Qué es?** No es un solo programa, sino una **infraestructura distribuida** de servidores (contenedores Docker) que trabajan juntos. Es una red **privada y permisionada**, lo que significa que solo los miembros invitados pueden entrar y operar, como en un club exclusivo.
*   **¿Para qué sirve?** Para crear un registro de eventos (transacciones) que sea **compartido, inmutable y verificable** por todos los miembros autorizados. Es la base de la confianza digital del sistema.

#### **2. Los Nodos (Los Funcionarios de la Notaría)**
La notaría tiene diferentes tipos de "funcionarios", cada uno con un trabajo específico.

*   **Peers (Pares):**
    *   **¿Qué son?** Son los "escribanos" o "archivadores" de la red. Cada organización (como la UTN) tiene al menos uno.
    *   **¿Para qué sirven?** Tienen dos trabajos cruciales:
        1.  **Almacenar el Ledger:** Guardan una copia completa del libro de contabilidad.
        2.  **Ejecutar el Chaincode:** Son los únicos que pueden "leer" las reglas del negocio y validar si una transacción propuesta es correcta.
*   **Orderer (Ordenador):**
    *   **¿Qué es?** Es el "notario principal" o el "juez de paz" de la red.
    *   **¿Para qué sirve?** Su única misión es recibir las transacciones ya validadas por los Peers, ponerlas en **orden cronológico** y empaquetarlas en bloques sellados. Luego, reparte estos bloques a todos los Peers para que los añadan a su copia del libro. **El Orderer garantiza que todos tengan la misma historia en el mismo orden.**
*   **CA (Autoridad de Certificación):**
    *   **¿Qué es?** Es la "oficina de credenciales" interna de la notaría. Cada organización tiene la suya.
    *   **¿Para qué sirve?** Emite y gestiona las **identidades digitales** (certificados X.509) de todos los participantes (Peers, Orderers, usuarios, aplicaciones). Es la que dice "Doy fe de que este peer pertenece a la UTN" o "Doy fe de que esta aplicación tiene permiso para emitir credenciales". **Es la base de la seguridad y los permisos.**

#### **3. El Ledger (El Libro de Contabilidad)**
*   **¿Qué es?** Es el libro de contabilidad digital que cada Peer almacena. Es la "fuente de la verdad". Se compone de dos partes:
    1.  **La Cadena de Bloques (Blockchain):**
        *   **¿Qué es?** Un archivo de registro **solo de adición**, un historial de todas las transacciones que han ocurrido, encadenadas criptográficamente.
        *   **¿Para qué sirve?** Proporciona la **inmutabilidad** y la **trazabilidad**. Permite auditar la historia completa de cualquier credencial.
        *   **¿Dónde se guarda?** Físicamente, en el sistema de archivos del contenedor Docker del Peer, en una ruta como `/var/hyperledger/production/ledgersData/chains/chains/mychannel/`.
    2.  **El Estado Mundial (World State):**
        *   **¿Qué es?** Una base de datos que contiene el **valor actual y final** de todos los activos del ledger. No guarda la historia, solo la "foto" del presente.
        *   **¿Para qué sirve?** Para realizar **consultas rápidas y eficientes**. Cuando pides los datos de "credencial01", el Peer no lee toda la cadena de bloques, sino que busca la última versión en esta base de datos.
        *   **¿Dónde se guarda?** En nuestro caso, lo configuramos para usar **CouchDB**. Esto significa que los datos se guardan en un contenedor Docker separado de CouchDB, que está vinculado al Peer. Podemos acceder a estos datos directamente a través de la interfaz web de CouchDB (ej. `http://localhost:5984/_utils/`).

#### **4. El Chaincode (Las Reglas de la Notaría)**
*   **¿Qué es?** Es el "reglamento interno" de la notaría, escrito en código (en nuestro caso, Go). Es el equivalente a un Smart Contract.
*   **¿Para qué sirve?** Define:
    *   **La Estructura de Datos:** Cómo es una "credencial" (qué campos tiene: ID, Alumno, Programa, etc.).
    *   **Las Funciones Válidas:** Qué operaciones se pueden realizar (`CreateAsset`, `ReadAsset`).
    *   **La Lógica de Validación:** Las condiciones que debe cumplir una transacción para ser válida (ej. "Para crear una credencial, el ID no debe existir previamente y el emisor debe ser Org1").
*   **¿Dónde se guarda?** El código del chaincode se **instala** en el sistema de archivos de cada Peer. Cuando se ejecuta, se lanza en su propio contenedor Docker seguro, vinculado al Peer.

#### **5. El Canal (La Sala de Reuniones Privada)**
*   **¿Qué es?** Es una "sub-red" privada dentro de la red Fabric. En nuestro caso, creamos `mychannel`.
*   **¿Para qué sirve?** Para la **privacidad y el aislamiento**. Solo los miembros de un canal pueden ver las transacciones y los datos de ese canal. Cada canal tiene su propio ledger independiente. Si la UTN tuviera otro canal con el Ministerio de Educación, las empresas de `mychannel` no podrían ver esas transacciones.
```
**Respuesta esperada:** Un objeto JSON con los detalles de la credencial.

```json
{"ID":"credencial01","Color":"Azul","Size":1,"Owner":"Marcelo","AppraisedValue":2024}
```
