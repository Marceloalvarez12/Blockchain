'use strict';

const express = require('express');
const { Gateway, Wallets } = require('fabric-network');
const path = require('path');
const fs = require('fs');

const app = express();
const port = 3000; // El puerto donde correrá esta API Gateway

// Middleware para que Express pueda entender y procesar cuerpos de petición en formato JSON
app.use(express.json());

/**
 * Función de ayuda para conectar al gateway de Hyperledger Fabric.
 * Reutiliza la lógica de conexión para no repetirla en cada endpoint.
 * @param {string} user - El nombre de la identidad a usar desde la billetera (ej. 'appUser').
 * @returns {Promise<{contract: import('fabric-network').Contract, gateway: import('fabric-network').Gateway}>}
 */
async function getContract(user) {
    try {
        // Cargar el perfil de conexión (el "mapa" de la red) desde el archivo JSON
        const ccpPath = path.resolve(__dirname, 'connection-org1.json');
        const ccp = JSON.parse(fs.readFileSync(ccpPath, 'utf8'));

        // Cargar la billetera (wallet) desde el sistema de archivos
        const walletPath = path.join(__dirname, 'wallet');
        const wallet = await Wallets.newFileSystemWallet(walletPath);

        // Verificar si la identidad del usuario existe en la billetera
        const identity = await wallet.get(user);
        if (!identity) {
            throw new Error(`La identidad para el usuario "${user}" no existe en la billetera. Asegúrate de haber ejecutado los scripts de registro (enrollAdmin, registerUser).`);
        }

        // Crear una nueva conexión de gateway y conectarse a la red
        const gateway = new Gateway();
        // Usamos la identidad cargada para conectar
        await gateway.connect(ccp, { wallet, identity: user, discovery: { enabled: true, asLocalhost: true } });
        
        // Obtener el canal y el contrato con el que queremos interactuar
        const network = await gateway.getNetwork('mychannel'); // CAMBIA a 'canalnuevo' si estás usando ese
        const contract = network.getContract('basic'); // CAMBIA si tu chaincode tiene otro nombre
        
        // Devolver el contrato y el gateway para poder usarlos y desconectarse después
        return { contract, gateway };
    } catch (error) {
        console.error(`Error al conectar al gateway de Fabric: ${error}`);
        throw error; // Relanzar el error para que el endpoint lo capture
    }
}

// --- Endpoints de la API ---

/**
 * Endpoint para realizar QUERIES (lecturas) al chaincode.
 * Es un GET y recibe los parámetros en la URL.
 */
app.get('/query/:func/:args', async (req, res) => {
    const { func, args } = req.params;
    console.log(`--> Petición GET recibida en /query: Función=${func}, Argumentos=${args}`);

    let gateway;
    try {
        const { contract, gateway: gw } = await getContract('appUser');
        gateway = gw; // Guardar referencia para desconectar en el finally

        console.log(`--> Evaluando transacción de solo lectura: ${func} con argumentos: ${args}`);
        const resultBytes = await contract.evaluateTransaction(func, args);
        
        const resultString = resultBytes.toString();
        // Si el resultado es vacío, devolvemos un objeto vacío en lugar de un error de parseo
        const resultJson = resultString ? JSON.parse(resultString) : {}; 

        res.status(200).json(resultJson);
    } catch (error) {
        console.error(`Fallo al evaluar la transacción: ${error}`);
        res.status(500).json({ success: false, error: error.message });
    } finally {
        if (gateway) {
            gateway.disconnect();
        }
    }
});

/**
 * Endpoint para realizar INVOKES (escrituras) al chaincode.
 * Es un POST y recibe los parámetros en el cuerpo (body) de la petición.
 */
app.post('/invoke', async (req, res) => {
    const { func, args } = req.body;
    console.log(`--> Petición POST recibida en /invoke: Función=${func}, Argumentos=${args}`);

    if (!func || !args || !Array.isArray(args)) {
        return res.status(400).json({ error: 'El cuerpo de la petición debe ser un JSON con una propiedad "func" (string) y una propiedad "args" (array).' });
    }

    let gateway;
    try {
        const { contract, gateway: gw } = await getContract('appUser');
        gateway = gw;

        console.log(`--> Enviando transacción de escritura: ${func} con argumentos: ${args}`);
        // submitTransaction se encarga de todo el flujo (endoso, ordenamiento, commit)
        await contract.submitTransaction(func, ...args);
        
        res.status(201).json({ success: true, message: `Transacción "${func}" enviada y comprometida exitosamente.` });
    } catch (error) {
        console.error(`Fallo al enviar la transacción: ${error}`);
        // Los errores del chaincode a menudo vienen con detalles útiles
        res.status(500).json({ success: false, error: error.message });
    } finally {
        if (gateway) {
            gateway.disconnect();
        }
    }
});

// Iniciar el servidor Express
app.listen(port, () => {
    console.log(`✅ API Gateway para Hyperledger Fabric escuchando en http://localhost:${port}`);
    console.log('Presiona Ctrl+C para detener el servidor.');
});