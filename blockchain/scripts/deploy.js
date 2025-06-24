const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners(); // La primera cuenta de Hardhat
  console.log("Desplegando contratos con la cuenta:", deployer.address);

  // Esta será la cuenta que Django usará para firmar transacciones.
  // Para Hardhat Network, podemos usar la cuenta del deployer como owner inicial.
  // Para una testnet, deberás proveer una dirección específica controlada por tu backend.
  const initialOwnerAddress = deployer.address; // O una dirección específica para el owner

  const credencialNombre = "Credencial Institucional Digital";
  const credencialSimbolo = "CID";

  const CredencialAlumno = await hre.ethers.getContractFactory("CredencialAlumno");
  const credencialAlumno = await CredencialAlumno.deploy(credencialNombre, credencialSimbolo, initialOwnerAddress);

  // await credencialAlumno.deployed(); // Ya no es necesario con Hardhat-ethers v6+

  const contractAddress = await credencialAlumno.getAddress();
  console.log("Contrato CredencialAlumno desplegado en:", contractAddress);
  console.log("Owner del contrato (cuenta de Django debería ser esta):", initialOwnerAddress);

  // Guarda la dirección y el ABI para Django
  // (esto es un ejemplo, puedes hacerlo más robusto)
  const fs = require('fs');
  const contractsDir = __dirname + "/../../django_project/blockchain_data"; // Ajusta la ruta a tu proyecto Django

  if (!fs.existsSync(contractsDir)) {
      fs.mkdirSync(contractsDir, { recursive: true });
  }

  fs.writeFileSync(
      contractsDir + "/contract-address.json",
      JSON.stringify({ CredencialAlumno: contractAddress }, undefined, 2)
  );

  const CredencialAlumnoArtifact = hre.artifacts.readArtifactSync("CredencialAlumno");

  fs.writeFileSync(
      contractsDir + "/CredencialAlumno.json", // Este es el ABI
      JSON.stringify(CredencialAlumnoArtifact, null, 2)
  );
  console.log("Dirección del contrato y ABI guardados en django_project/blockchain_data");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });