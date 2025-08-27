// D:\...\fabric-api-gateway\enrollAdmin.js
'use strict';

const FabricCAServices = require('fabric-ca-client');
const { Wallets } = require('fabric-network');
const fs = require('fs');
const path = require('path');

async function main() {
    try {
        const ccpPath = path.resolve(__dirname, 'connection-org1.json');
        const ccp = JSON.parse(fs.readFileSync(ccpPath, 'utf8'));

        const caInfo = ccp.certificateAuthorities['ca.org1.example.com'];
        const caTLSCACerts = caInfo.tlsCACerts.pem;
        const ca = new FabricCAServices(caInfo.url, { trustedRoots: caTLSCACerts, verify: false }, caInfo.caName);

        const walletPath = path.join(process.cwd(), 'wallet');
        const wallet = await Wallets.newFileSystemWallet(walletPath);
        console.log(`Ruta de la billetera: ${walletPath}`);

        const identity = await wallet.get('admin');
        if (identity) {
            console.log('La identidad para el usuario "admin" ya existe en la billetera.');
            return;
        }

        const enrollment = await ca.enroll({ enrollmentID: 'admin', enrollmentSecret: 'adminpw' });
        const x509Identity = {
            credentials: {
                certificate: enrollment.certificate,
                privateKey: enrollment.key.toBytes(),
            },
            mspId: 'Org1MSP',
            type: 'X.509',
        };

        await wallet.put('admin', x509Identity);
        console.log('Éxito: Se ha inscrito al usuario "admin" y se ha importado a la billetera.');

    } catch (error) {
        console.error(`Fallo al inscribir al usuario "admin": ${error}`);
        process.exit(1);
    }
}

main();