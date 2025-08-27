// D:\...\fabric-api-gateway\registerUser.js
'use strict';

const { Wallets } = require('fabric-network');
const FabricCAServices = require('fabric-ca-client');
const fs = require('fs');
const path = require('path');

async function main() {
    try {
        const ccpPath = path.resolve(__dirname, 'connection-org1.json');
        const ccp = JSON.parse(fs.readFileSync(ccpPath, 'utf8'));

        const caURL = ccp.certificateAuthorities['ca.org1.example.com'].url;
        const ca = new FabricCAServices(caURL);

        const walletPath = path.join(process.cwd(), 'wallet');
        const wallet = await Wallets.newFileSystemWallet(walletPath);
        console.log(`Ruta de la billetera: ${walletPath}`);

        const userIdentity = await wallet.get('appUser');
        if (userIdentity) {
            console.log('La identidad para el usuario "appUser" ya existe en la billetera.');
            return;
        }

        const adminIdentity = await wallet.get('admin');
        if (!adminIdentity) {
            console.log('La identidad del "admin" no existe. Ejecuta enrollAdmin.js primero.');
            return;
        }

        const provider = wallet.getProviderRegistry().getProvider(adminIdentity.type);
        const adminUser = await provider.getUserContext(adminIdentity, 'admin');

        const secret = await ca.register({
            affiliation: 'org1.department1',
            enrollmentID: 'appUser',
            role: 'client'
        }, adminUser);
        const enrollment = await ca.enroll({
            enrollmentID: 'appUser',
            enrollmentSecret: secret
        });
        const x509Identity = {
            credentials: {
                certificate: enrollment.certificate,
                privateKey: enrollment.key.toBytes(),
            },
            mspId: 'Org1MSP',
            type: 'X.509',
        };
        await wallet.put('appUser', x509Identity);
        console.log('Éxito: Se ha registrado e inscrito al usuario "appUser" y se ha importado a la billetera.');

    } catch (error) {
        console.error(`Fallo al registrar al usuario "appUser": ${error}`);
        process.exit(1);
    }
}

main();