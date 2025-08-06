
El objetivo es abstraer la complejidad de la infraestructura de Fabric y darle instrucciones claras sobre **cómo interactuar con la red blockchain ya funcional**. Este documento asume que tú, como administrador de la blockchain, ya has desplegado la red.


# 📖 Guía de Integración de Backend con la Red de Credenciales Hyperledger Fabric

¡Hola, Desarrollador de Backend!

Bienvenido al proyecto de credenciales digitales. Ya hemos desplegado y configurado una red blockchain privada utilizando **Hyperledger Fabric**. Tu misión, si decides aceptarla, es construir el backend (API) que interactuará con esta red para emitir y verificar credenciales.

Esta guía te explicará cómo funciona la red a un alto nivel y te dará las herramientas y comandos necesarios para interactuar con ella.

## 🏛️ Arquitectura Simplificada

No necesitas ser un experto en Fabric, pero es útil entender el flujo:

```mermaid
graph TD
    A[Tu Backend (API)] -->|Llama a un Script o usa un SDK| B{Aplicación Cliente de Fabric};
    B -->|Se conecta a la red usando una identidad| C(Nodos Peer de Fabric);
    C -->|Ejecuta funciones en el| D[(Chaincode)];
    D -->|Lee/Escribe en| E[((Ledger - Blockchain))];
```

Tu **backend actuará como el cliente** que envía órdenes al `Chaincode` (nuestro "smart contract"). El chaincode que está actualmente desplegado se llama `basic` y vive en un canal llamado `mychannel`.

## ⚙️ El Chaincode: Tus Funciones Disponibles

El chaincode de ejemplo que está desplegado tiene la estructura de un "activo" genérico. Mapearemos los datos de nuestras credenciales a esta estructura. La función principal que usarás es:

`CreateAsset(id, color, size, owner, appraisedValue)`

-   `id` (string): Un identificador único para la credencial (ej: `"credencial-marcelo-001"`).
-   `color` (string): Puedes usar este campo para el **Programa del Alumno** (ej: `"Ing. Blockchain"`).
-   `size` (int): Puedes usarlo para el **ID del Alumno** (ej: `2024001`).
-   `owner` (string): El **Nombre del Alumno** (ej: `"Marcelo"`).
-   `appraisedValue` (int): Puedes usarlo para la **Fecha de Emisión** en formato timestamp o AAAA (ej: `2024`).

**Importante:** En una fase futura, personalizaremos este chaincode para que tenga campos más apropiados (`idAlumno`, `programa`, etc.), pero por ahora, trabajaremos con esta estructura de ejemplo.

## 🚀 Cómo Interactuar con la Red (El Kit de Herramientas del Backend)

Para interactuar, necesitarás ejecutar comandos desde una terminal. Hemos preparado un "entorno de prueba" usando la **CLI (Command Line Interface)** de Fabric, que simula lo que un SDK haría programáticamente.

### ✅ Prerrequisitos para tu Entorno

Asegúrate de tener en tu máquina:
- **Git:** Para tener acceso a una terminal Bash.

### 📜 Pasos para la Interacción

**1. Abre una Terminal Git Bash:**
Navega a la carpeta `fabric-samples/test-network` de este proyecto. Todas las interacciones se harán desde ahí.
```bash
cd /ruta/a/fabric-samples/test-network
```

**2. Adopta la Identidad de la Institución (Org1):**
La red es "permisionada", por lo que debes actuar en nombre de una organización. Cada vez que abras una nueva terminal, ejecuta este bloque de código para "iniciar sesión" como el Administrador de Org1.

```bash
# Exportar las variables de identidad de Admin@Org1
export PATH=${PWD}/../../bin:$PATH
export FABRIC_CFG_PATH=${PWD}/../config/
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051
```
*Verifica que funcionó ejecutando `peer version`. Deberías ver la versión instalada.*

**3. Interactuar con el Chaincode:**

#### **Para EMITIR una nueva credencial (Transacción de Escritura)**

Usa el comando `peer chaincode invoke`. Este es el comando completo:

```bash
peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" -C mychannel -n basic --peerAddresses localhost:7051 --tlsRootCertFiles "${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt" --peerAddresses localhost:9051 --tlsRootCertFiles "${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt" -c '{"function":"CreateAsset","Args":["credencial002", "Ingenieria de Software", "12345", "Ana Lopez", "2024"]}'
```

**Parámetros Clave en la llamada:**
-   `-C mychannel`: El canal donde se ejecuta la transacción.
-   `-n basic`: El nombre del chaincode.
-   `-c '{"function":"CreateAsset","Args":[...]}':` La función a llamar y sus argumentos en formato JSON. **Aquí es donde tu backend construirá el JSON con los datos del alumno.**

**Respuesta Esperada:**
```
INFO [chaincodeCmd] chaincodeInvokeOrQuery -> Chaincode invoke successful. result: status:200
```

#### **Para VERIFICAR una credencial (Transacción de Lectura)**

Usa el comando `peer chaincode query`. Es mucho más simple.

```bash
# Para verificar una credencial específica por su ID
peer chaincode query -C mychannel -n basic -c '{"Args":["ReadAsset","credencial002"]}'

# Para ver TODAS las credenciales (útil para depuración)
peer chaincode query -C mychannel -n basic -c '{"Args":["GetAllAssets"]}'
```
**Respuesta Esperada (para `ReadAsset`):**
```json
{"ID":"credencial002","color":"Ingenieria de Software","size":12345,"owner":"Ana Lopez","appraisedValue":2024}
```

## 🎯 Tu Tarea como Desarrollador de Backend

Tu objetivo es crear una API que envuelva estos comandos de terminal.

1.  **Crea un Endpoint `POST /api/credenciales`:**
    -   Debe aceptar un cuerpo JSON con los datos de una nueva credencial (ej: `idAlumno`, `nombre`, `programa`).
    -   Dentro del endpoint, tu código debe:
        a.  Construir el string JSON de `Args` para la función `CreateAsset`.
        b.  Ejecutar el comando `peer chaincode invoke` como un **subproceso** del sistema operativo.
        c.  Capturar la salida del comando.
        d.  Devolver una respuesta de éxito (`201 Created`) si el comando funcionó, o un error (`500`) si falló.

2.  **Crea un Endpoint `GET /api/credenciales/:id`:**
    -   Debe aceptar el ID de una credencial en la URL.
    -   Tu código debe ejecutar el comando `peer chaincode query` con `ReadAsset` y el ID proporcionado.
    -   Capturar la salida JSON, parsearla y devolverla al cliente.

¡Mucha suerte! La red blockchain está lista y esperándote. Cualquier duda sobre Fabric, házmela saber.

---