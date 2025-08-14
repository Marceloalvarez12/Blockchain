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

# Resumen del Proyecto: Arquitectura de la Infraestructura Blockchain (Hyperledger Fabric)

Este documento describe los componentes, el flujo de datos, la estructura del ledger y **todos los pasos** (de punta a punta) para levantar la red, desplegar el chaincode y habilitar el inicio de sesión con identidades de Fabric en el sistema de **credenciales digitales**.

---

## 1. Visión General

La plataforma seleccionada es **Hyperledger Fabric v2.5**, un framework de la Linux Foundation para soluciones empresariales.

- **Red privada y permisionada**: solo entidades autorizadas participan.
- **Topología de prueba**:
  - **2 Organizaciones**: Org1 (Emisora) y Org2 (Verificadora).
  - **1 Servicio de Ordenamiento** (Raft).
  - **1 Canal**: `mychannel`.

---

## 2. Componentes Principales

La red se compone de **contenedores Docker**.

### 2.1. Peers
- Mantienen el ledger (bloques + world state).
- Ejecutan chaincode y **endosan** transacciones.

### 2.2. Orderer
- Recibe transacciones endosadas, las ordena en bloques y las distribuye.

### 2.3. CA (Certificate Authority)
- Emite certificados X.509 y gestiona el **MSP**.

---

## 3. El Ledger

### 3.1. Blockchain (histórico)
- Cadena inmutable de bloques con transacciones y sus read/write sets.

### 3.2. World State (estado actual)
- Base de datos **clave-valor** (p.ej. CouchDB).

```json
{
  "ID": "credencial01",
  "Owner": "Marcelo",
  "Programa": "Ing. Blockchain"
}
```

---

## 4. Chaincode (Smart Contract)

- Encapsula la lógica de negocio (Go).
- Define estructura de activos y funciones (CreateAsset, ReadAsset, etc.).
- Ciclo de vida: package → install → approve → commit → invoke.

---

## 5. Canales

- Aíslan datos entre miembros.
- Cada canal tiene su propio ledger y chaincode instanciado.
- En este proyecto se usa `mychannel`.

---

## 6. Identidades y Login

### 6.1. Registro de Usuario (Admin)
- Admin registra al usuario en la CA.
- La CA emite certificado X.509 (identidad Fabric).
- Se asocia identidad con datos del usuario (y opcionalmente con la wallet pública si hay puente con Ethereum/Metamask).

### 6.2. Inicio de Sesión (User)
- En el frontend, el usuario elige "Iniciar sesión".
- La app solicita firmar un mensaje (con certificado Fabric o wallet).
- El backend verifica la firma contra el certificado emitido por la CA (MSP).
- Si es válido, se crea sesión (JWT/Token) y se accede a su información on-chain.

**Versión simple para no técnicos:**
- **Registro**: el admin te crea una "credencial digital" (certificado).
- **Login**: comprobás tu identidad firmando; si coincide, entrás.

---

## 7. Estructura de Credenciales (Ejemplo en Ledger)

```json
{
  "CredencialID": "CRED-001",
  "Usuario": "Marcelo Alvarez",
  "Certificado": "-----BEGIN CERTIFICATE-----...-----END CERTIFICATE-----",
  "Wallet": "0xAbC1234Ef...",
  "Programa": "Ingeniería Blockchain",
  "Estado": "Vigente"
}
```

---

## 8. Prerrequisitos (Windows/Linux/macOS)

- Docker y Docker Compose funcionando.
- Fabric binaries que coincidan con las imágenes Docker.
- Recomendado: v2.5.x para peer/orderer y v1.5.x para Fabric-CA.
- `jq` instalado (para parsear JSON en scripts).
- Go instalado si el chaincode es Go.
- Git Bash o WSL recomendados en Windows.
- Variables de entorno y PATH apuntando a `fabric-samples/bin`.

### 8.1. Instalación rápida de utilidades

**Windows (choco):**
```powershell
choco install -y jq golang
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y jq golang-go
```

**PATH (PowerShell):**
```powershell
$env:PATH = "C:\fabric-project\fabric-samples\bin;" + $env:PATH
```

**PATH (Git Bash/WSL):**
```bash
export PATH=/c/fabric-project/fabric-samples/bin:$PATH
```

---

## 9. Preparar el proyecto

```bash
# Clonar fabric-samples
git clone https://github.com/hyperledger/fabric-samples.git
cd fabric-samples

# (Opcional) Checkout a la rama/tag compatible
git checkout v2.5.0

# Verificar binarios
peer version
orderer version
fabric-ca-client version
```

---

## 10. Levantar la Red y Crear Canal

```bash
cd fabric-samples/test-network

# Limpiar todo
./network.sh down

# (Opcional) Reconstruir imágenes/volúmenes
docker system prune -af
docker volume prune -f

# Levantar con CouchDB y CA
./network.sh up createChannel -ca -s couchdb -c mychannel
```

**Salida esperada:**
- Contenedores: `orderer.example.com`, `peer0.org1.example.com`, `peer0.org2.example.com`, `couchdb0`, `couchdb1`, `ca_org1`, `ca_org2`.
- Canal `mychannel` creado.
- Peers unidos al canal.

> **Nota**: Si aparece error de conexión a `localhost:7051` en Windows, usar Git Bash/WSL y evitar conflictos IPv6 (`[::1]`).

---

## 11. Desplegar Chaincode (Go)

```bash
# Desde test-network
./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-go -ccl go
```

**Esto:**
- Empaqueta e instala chaincode en los peers.
- Aprueba y commitea la definición del chaincode en `mychannel`.

> **Solución de errores comunes:**
> - Si ves `go: command not found` → instalá Go y re-exportá PATH.
> - Si ves `jq: command not found` → instalá jq.

---

## 12. Probar el Chaincode

```bash
# Setear Org1
export PATH=${PWD}/../bin:$PATH
export FABRIC_CFG_PATH=$PWD/../config/
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051

# Init ledger
peer chaincode invoke -o localhost:7050 \
  --ordererTLSHostnameOverride orderer.example.com \
  --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
  -C mychannel -n basic \
  --peerAddresses localhost:7051 \
  --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt \
  --peerAddresses localhost:9051 \
  --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt \
  -c '{"Args":["InitLedger"]}'

# Consultar (query)
peer chaincode query -C mychannel -n basic -c '{"Args":["GetAllAssets"]}'
```

---

## 13. Guía Rápida - Comandos Esenciales

### Levantar la red completa:
```bash
cd fabric-samples/test-network
./network.sh down
./network.sh up createChannel -ca -s couchdb -c mychannel
./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-go -ccl go
```

### Variables de entorno para Org1:
```bash
export PATH=${PWD}/../bin:$PATH
export FABRIC_CFG_PATH=$PWD/../config/
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051
```

### Comandos básicos de prueba:
```bash
# Inicializar ledger
peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic --peerAddresses localhost:7051 --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt --peerAddresses localhost:9051 --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt -c '{"Args":["InitLedger"]}'

# Consultar todos los activos
peer chaincode query -C mychannel -n basic -c '{"Args":["GetAllAssets"]}'
```

---


## 14. Recursos Adicionales

- [Documentación oficial de Hyperledger Fabric](https://hyperledger-fabric.readthedocs.io/)
- [Fabric Samples](https://github.com/hyperledger/fabric-samples)
- [Guía de desarrollo de chaincode](https://hyperledger-fabric.readthedocs.io/en/latest/developapps/developing_applications.html)
- [Configuración de red](https://hyperledger-fabric.readthedocs.io/en/latest/network/network.html)
